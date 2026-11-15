"""Executa verificações autenticadas somente de leitura no Xano."""

import argparse
import asyncio
import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from biblioteca_mais_nova.xano_client import (
    XanoClient,
    XanoConfigurationError,
    XanoRequestError,
    XanoResponseError,
    XanoTimeoutError,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


PROFILE_CHECKS = {
    "estudante": (
        "XANO_SMOKE_ESTUDANTE_EMAIL",
        "XANO_SMOKE_ESTUDANTE_SENHA",
        (
            "/auth/me",
            "/minhas/emprestimos",
            "/minhas/solicitacoes",
            "/minhas/reservas",
        ),
    ),
    "bibliotecario": (
        "XANO_SMOKE_BIBLIOTECARIO_EMAIL",
        "XANO_SMOKE_BIBLIOTECARIO_SENHA",
        (
            "/auth/me",
            "/admin/acervo",
            "/admin/solicitacoes",
            "/admin/reservas",
            "/admin/emprestimos",
        ),
    ),
    "admin": (
        "XANO_SMOKE_ADMIN_EMAIL",
        "XANO_SMOKE_ADMIN_SENHA",
        (
            "/auth/me",
            "/admin/acervo",
            "/admin/solicitacoes",
            "/admin/reservas",
            "/admin/emprestimos",
            "/admin/usuarios",
        ),
    ),
}


@dataclass(frozen=True)
class SmokeResult:
    profile: str
    path: str
    status: str
    count: int | None = None


def _count_records(payload: Any) -> int | None:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        return 1 if payload else 0
    return None


def _format_result(result: SmokeResult) -> str:
    line = (
        f"perfil={result.profile} rota={result.path} "
        f"status={result.status}"
    )
    if result.count is not None:
        line += f" quantidade={result.count}"
    return line


async def run_smoke(
    client: XanoClient,
    environment: Mapping[str, str],
    *,
    emit: Callable[[str], None] = print,
) -> list[SmokeResult]:
    results: list[SmokeResult] = []

    def record(result: SmokeResult) -> None:
        results.append(result)
        emit(_format_result(result))

    for profile, (email_key, password_key, paths) in PROFILE_CHECKS.items():
        email = environment.get(email_key, "").strip()
        password = environment.get(password_key, "")
        if not email or not password:
            emit(f"perfil={profile} status=ignorado")
            continue

        try:
            login_response = await client.request(
                "POST",
                "/auth/login",
                json={"email": email, "senha": password},
            )
        except XanoResponseError as error:
            record(SmokeResult(profile, "/auth/login", str(error.status_code)))
            continue
        except XanoTimeoutError:
            status = "timeout"
            record(SmokeResult(profile, "/auth/login", status))
            continue
        except XanoRequestError:
            status = "erro"
            record(SmokeResult(profile, "/auth/login", status))
            continue

        try:
            session = login_response.json()
        except (json.JSONDecodeError, ValueError):
            session = None
        token = session.get("authToken") if isinstance(session, dict) else None
        if not isinstance(token, str) or not token:
            record(SmokeResult(profile, "/auth/login", str(login_response.status_code)))
            continue

        record(SmokeResult(profile, "/auth/login", str(login_response.status_code)))
        for path in paths:
            try:
                response = await client.request("GET", path, token=token)
            except XanoResponseError as error:
                record(SmokeResult(profile, path, str(error.status_code)))
                continue
            except XanoTimeoutError:
                status = "timeout"
                record(SmokeResult(profile, path, status))
                continue
            except XanoRequestError:
                status = "erro"
                record(SmokeResult(profile, path, status))
                continue

            try:
                payload = response.json()
            except (json.JSONDecodeError, ValueError):
                payload = None
            record(
                SmokeResult(
                    profile,
                    path,
                    str(response.status_code),
                    _count_records(payload),
                )
            )

    return results


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smoke_xano.py",
        description=(
            "Faz login e consultas GET de leitura no Xano. "
            "As credenciais vêm somente das variáveis do terminal; "
            "nenhum token, senha, e-mail ou URL é exibido."
        ),
        epilog=(
            "Exemplo no PowerShell (substitua pelos dados de teste, "
            "sem salvá-los em arquivo):\n"
            '  $env:XANO_SMOKE_ESTUDANTE_EMAIL = "aluno@exemplo.invalid"\n'
            '  $env:XANO_SMOKE_ESTUDANTE_SENHA = "<senha de teste>"\n'
            '  $env:XANO_SMOKE_BIBLIOTECARIO_EMAIL = "bib@exemplo.invalid"\n'
            '  $env:XANO_SMOKE_BIBLIOTECARIO_SENHA = "<senha de teste>"\n'
            '  $env:XANO_SMOKE_ADMIN_EMAIL = "admin@exemplo.invalid"\n'
            '  $env:XANO_SMOKE_ADMIN_SENHA = "<senha de teste>"\n'
            "  .\\.venv\\Scripts\\python.exe -m scripts.smoke_xano\n"
            "Perfis sem ambos os valores são ignorados. "
            "O endereço XANO_API_BASE_URL é lido da configuração local. "
            "A senha deve ficar somente no ambiente desta sessão do terminal."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    _build_parser().parse_args(argv)
    terminal_environment = os.environ.copy()
    load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)
    try:
        client = XanoClient.from_environment(timeout=15.0)
    except XanoConfigurationError:
        print("status=configuracao_indisponivel")
        return 2

    results = asyncio.run(run_smoke(client, terminal_environment))
    if not results:
        print("status=nenhum_perfil_configurado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
