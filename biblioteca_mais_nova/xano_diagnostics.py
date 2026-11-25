"""Diagnóstico estrutural, somente leitura, das respostas autorizadas do Xano."""

import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypedDict

import httpx

from biblioteca_mais_nova.catalog import (
    _parse_admin_catalog_entry,
    _parse_category,
    _parse_public_catalog_entry,
)
from biblioteca_mais_nova.circulation import (
    _parse_admin_loan,
    _parse_admin_reservation,
    _parse_loan,
    _parse_request,
    _parse_reservation,
)
from biblioteca_mais_nova.response_parsing import extract_xano_list
from biblioteca_mais_nova.user_admin import _parse_librarian
from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoInvalidResponseError,
    XanoRequestError,
    XanoResponseError,
    XanoTimeoutError,
    parse_xano_response_json,
    registrar_resultado_xano,
)


class XanoDiagnosticResult(TypedDict):
    name: str
    status: str
    duration_ms: int
    top_type: str
    record_count: int
    fields: str
    validation: str
    problematic_fields: str
    reason: str
    reference: str


@dataclass(frozen=True)
class _Endpoint:
    name: str
    path: str
    parser: Callable[[object], object]
    authenticated: bool = True
    identifier: Callable[[dict[str, object]], object] | None = None


def _title_identifier(record: dict[str, object]) -> object:
    title = record.get("titulo")
    return title.get("id") if isinstance(title, dict) else None


def _endpoints_for_profile(profile: str) -> list[_Endpoint]:
    public = [
        _Endpoint(
            "Catálogo público",
            "/catalogo/titulos",
            _parse_public_catalog_entry,
            authenticated=False,
            identifier=_title_identifier,
        ),
        _Endpoint(
            "Categorias públicas",
            "/catalogo/categorias",
            _parse_category,
            authenticated=False,
        ),
    ]
    if profile == "estudante":
        return [
            *public,
            _Endpoint("Meus empréstimos", "/minhas/emprestimos", _parse_loan),
            _Endpoint(
                "Minhas solicitações",
                "/minhas/solicitacoes",
                _parse_request,
            ),
            _Endpoint(
                "Minhas reservas",
                "/minhas/reservas",
                _parse_reservation,
            ),
        ]
    if profile in {"bibliotecario", "admin"}:
        staff = [
            *public,
            _Endpoint("Acervo administrativo", "/admin/acervo", _parse_admin_catalog_entry),
            _Endpoint("Solicitações da equipe", "/admin/solicitacoes", _parse_request),
            _Endpoint(
                "Reservas da equipe",
                "/admin/reservas",
                _parse_admin_reservation,
            ),
            _Endpoint("Empréstimos da equipe", "/admin/emprestimos", _parse_admin_loan),
        ]
        if profile == "admin":
            staff.append(
                _Endpoint("Contas bibliotecárias", "/admin/usuarios", _parse_librarian)
            )
        return staff
    raise ValueError("O perfil não permite executar o diagnóstico.")


def _type_name(value: object) -> str:
    if value is None:
        return "nulo"
    if type(value) is bool:
        return "booleano"
    if type(value) is int:
        return "inteiro"
    if type(value) is float:
        return "decimal"
    if isinstance(value, str):
        return "texto"
    if isinstance(value, list):
        return "lista"
    if isinstance(value, dict):
        return "objeto"
    return "desconhecido"


def _safe_field_name(value: object) -> str:
    name = str(value)
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]{0,63}", name):
        return name
    return "campo"


def _valid_identifier(value: object) -> bool:
    if type(value) is int:
        return value > 0
    if isinstance(value, str) and re.fullmatch(r"[0-9]+", value.strip()):
        return int(value.strip()) > 0
    return False


def _field_summary(value: object) -> str:
    if not isinstance(value, dict):
        return "—"

    fields: list[str] = []

    def collect(record: dict[object, object], prefix: str = "", depth: int = 0) -> None:
        for key, field_value in sorted(record.items(), key=lambda item: str(item[0])):
            name = _safe_field_name(key)
            path = f"{prefix}.{name}" if prefix else name
            fields.append(f"{path}: {_type_name(field_value)}")
            if depth >= 2:
                continue
            if isinstance(field_value, dict):
                collect(field_value, path, depth + 1)
            elif (
                isinstance(field_value, list)
                and field_value
                and isinstance(field_value[0], dict)
            ):
                collect(field_value[0], f"{path}[]", depth + 1)
            if len(fields) >= 24:
                return

    collect(value)
    return "; ".join(fields) if fields else "—"


def _invalid_result(
    endpoint: _Endpoint,
    *,
    status: str,
    duration_ms: int,
    reason: str,
    top_type: str = "indisponível",
    record_count: int = 0,
    fields: str = "—",
    problematic_fields: str = "resposta",
    reference: str = "—",
) -> XanoDiagnosticResult:
    return {
        "name": endpoint.name,
        "status": status,
        "duration_ms": duration_ms,
        "top_type": top_type,
        "record_count": record_count,
        "fields": fields,
        "validation": "inválida",
        "problematic_fields": problematic_fields,
        "reason": reason,
        "reference": reference,
    }


def _inspect_payload(
    endpoint: _Endpoint,
    payload: object,
    *,
    status: str,
    duration_ms: int,
) -> tuple[XanoDiagnosticResult, bool, str | None]:
    top_type = _type_name(payload)
    try:
        records = extract_xano_list(payload)
    except XanoInvalidResponseError as error:
        result = _invalid_result(
            endpoint,
            status=status,
            duration_ms=duration_ms,
            reason="o topo não é uma lista nem um envelope reconhecido",
            top_type=top_type,
        )
        return result, False, error.reference

    first_record = records[0] if records else None
    fields = _field_summary(first_record)
    for index, record in enumerate(records):
        problematic_fields = "registro"
        invalid_reason = f"o registro {index + 1} não é um objeto"
        try:
            if not isinstance(record, dict):
                raise XanoInvalidResponseError()
            invalid_reason = (
                f"o identificador do registro {index + 1} é inválido"
            )
            identifier = (
                endpoint.identifier(record)
                if endpoint.identifier is not None
                else record.get("id")
            )
            if not _valid_identifier(identifier):
                problematic_fields = "id"
                raise XanoInvalidResponseError()
            invalid_reason = (
                f"o registro {index + 1} não corresponde ao contrato"
            )
            endpoint.parser(record)
        except XanoInvalidResponseError as error:
            return (
                _invalid_result(
                    endpoint,
                    status=status,
                    duration_ms=duration_ms,
                    reason=invalid_reason,
                    top_type=top_type,
                    record_count=len(records),
                    fields=fields,
                    problematic_fields=problematic_fields,
                ),
                False,
                error.reference,
            )

    return (
        {
            "name": endpoint.name,
            "status": status,
            "duration_ms": duration_ms,
            "top_type": top_type,
            "record_count": len(records),
            "fields": fields,
            "validation": "válida",
            "problematic_fields": "—",
            "reason": "—",
            "reference": "—",
        },
        True,
        None,
    )


def _failure_result(
    endpoint: _Endpoint,
    *,
    status: str,
    duration_ms: int,
    reason: str,
    reference: str | None,
) -> XanoDiagnosticResult:
    return _invalid_result(
        endpoint,
        status=status,
        duration_ms=duration_ms,
        reason=reason,
        reference=reference or "—",
    )


async def diagnose_xano(
    profile: str,
    token: str,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[XanoDiagnosticResult]:
    endpoints = _endpoints_for_profile(profile)
    results: list[XanoDiagnosticResult] = []

    for endpoint in endpoints:
        started_at = time.perf_counter()
        response: httpx.Response | None = None
        try:
            client = XanoClient.from_environment(transport=transport)
            response = await client.request(
                "GET",
                endpoint.path,
                token=token if endpoint.authenticated else None,
            )
            status = f"HTTP {response.status_code}"
            payload = parse_xano_response_json(response)
        except XanoResponseError as error:
            duration_ms = round((time.perf_counter() - started_at) * 1000)
            results.append(
                _failure_result(
                    endpoint,
                    status=f"HTTP {error.status_code}",
                    duration_ms=duration_ms,
                    reason=f"consulta recusada pelo servidor (HTTP {error.status_code})",
                    reference=error.reference,
                )
            )
            continue
        except XanoConfigurationError:
            duration_ms = round((time.perf_counter() - started_at) * 1000)
            results.append(
                _failure_result(
                    endpoint,
                    status="sem resposta",
                    duration_ms=duration_ms,
                    reason="configuração do cliente indisponível",
                    reference=None,
                )
            )
            continue
        except XanoRequestError as error:
            duration_ms = round((time.perf_counter() - started_at) * 1000)
            if response is not None:
                reason = "resposta JSON ilegível"
                status = f"HTTP {response.status_code}"
            elif isinstance(error, XanoTimeoutError):
                reason = "tempo esgotado"
                status = "sem resposta"
            else:
                reason = "falha de conexão"
                status = "sem resposta"
            results.append(
                _failure_result(
                    endpoint,
                    status=status,
                    duration_ms=duration_ms,
                    reason=reason,
                    reference=error.reference,
                )
            )
            continue

        duration_ms = round((time.perf_counter() - started_at) * 1000)
        result, valid, reference = _inspect_payload(
            endpoint,
            payload,
            status=status,
            duration_ms=duration_ms,
        )
        if not valid:
            result["reference"] = reference or registrar_resultado_xano(
                action="testar_conexao",
                profile=profile,
                method="GET",
                path=endpoint.path,
                status=response.status_code,
                result="resposta 2xx com estrutura incompatível",
            )
        results.append(result)

    return results


def format_xano_diagnostic_report(
    results: list[XanoDiagnosticResult],
) -> str:
    lines = ["Diagnóstico Xano — somente leitura"]
    for result in results:
        lines.append(
            f"{result['name']}: {result['status']}; "
            f"{result['duration_ms']} ms; topo={result['top_type']}; "
            f"registros={result['record_count']}; campos={result['fields']}; "
            f"validação={result['validation']}; "
            f"campos problemáticos={result['problematic_fields']}; "
            f"motivo={result['reason']}; ref={result['reference']}"
        )
    return "\n".join(lines)
