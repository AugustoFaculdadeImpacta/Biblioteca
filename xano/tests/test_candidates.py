import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "table"
APIS = ROOT / "api" / "default"
OPENAPI = ROOT / "openapi.json"
API_DECLARATION = re.compile(
    r'(?m)^query\s+"([^"]+)"\s+verb=(GET|POST|PATCH|PUT|DELETE)'
)


def normalize_path(path):
    return re.sub(r"\{[^}]+\}", "{}", path)


def input_fields(source):
    match = re.search(r"\binput\s*\{", source)
    if not match:
        return set()
    start = match.end()
    depth = 1
    end = start
    while depth and end < len(source):
        if source[end] == "{":
            depth += 1
        elif source[end] == "}":
            depth -= 1
        end += 1
    return set(
        re.findall(
            r"^\s*(?:int|text|email|password|enum)\s+([A-Za-z_]\w*)",
            source[start : end - 1],
            re.MULTILINE,
        )
    )


class TestCandidateContracts(unittest.TestCase):
    def test_table_candidates_declare_primary_key_and_references(self):
        expected = {
            "usuario",
            "titulo",
            "categoria",
            "titulo_categoria",
            "exemplar",
            "solicitacao_emprestimo",
            "emprestimo",
            "reserva",
            "condicao_exemplar",
        }
        files = {path.stem: path for path in TABLES.glob("*.xs")}
        self.assertEqual(expected, set(files))

        for name, path in files.items():
            source = path.read_text(encoding="utf-8")
            self.assertRegex(source, rf"(?m)^table {re.escape(name)} \{{")
            self.assertRegex(source, r"(?s)schema \{\s*int id\b")

        all_sources = "\n".join(path.read_text(encoding="utf-8") for path in files.values())
        references = re.findall(r'\btable\s*=\s*"([^"]+)"', all_sources)
        self.assertTrue(references)
        self.assertLessEqual(set(references), expected)

    def test_approved_identity_and_catalog_rules_are_represented(self):
        user = (TABLES / "usuario.xs").read_text(encoding="utf-8")
        title = (TABLES / "titulo.xs").read_text(encoding="utf-8")
        copy = (TABLES / "exemplar.xs").read_text(encoding="utf-8")
        signup = (APIS / "auth" / "signup_POST.xs").read_text(encoding="utf-8")
        login = (APIS / "auth" / "login_POST.xs").read_text(encoding="utf-8")

        self.assertIn('type: "btree|unique", field: [{name: "email"', user)
        self.assertIn('enum perfil', user)
        self.assertIn('perfil : "estudante"', signup)
        self.assertIn('contains:" "', signup)
        self.assertIn('contains:" "', login)
        self.assertIn("password senha", signup)
        self.assertIn("text titulo filters=trim", title)
        self.assertIn("text autores filters=trim", title)
        self.assertIn('type: "btree|unique", field: [{name: "codigo_tombo"', copy)

    def test_admin_xanoscript_endpoints_require_auth_and_role(self):
        admin_files = list((APIS / "admin").glob("*.xs"))
        self.assertGreaterEqual(len(admin_files), 3)
        for path in admin_files:
            source = path.read_text(encoding="utf-8")
            self.assertIn('auth = "usuario"', source, path.name)
            self.assertIn('$usuario.perfil == "bibliotecario"', source, path.name)

    def test_xanoscript_candidate_delimiters_are_balanced(self):
        for path in ROOT.rglob("*.xs"):
            source = re.sub(r"(?m)//.*$", "", path.read_text(encoding="utf-8"))
            for opening, closing in [("{", "}"), ("[", "]"), ("(", ")")]:
                self.assertEqual(
                    source.count(opening),
                    source.count(closing),
                    f"Unbalanced {opening}{closing} in {path.relative_to(ROOT)}",
                )

    def test_openapi_json_has_documented_routes_and_protected_admin(self):
        document = json.loads(OPENAPI.read_text(encoding="utf-8"))
        self.assertEqual("3.1.0", document["openapi"])
        paths = document["paths"]
        required_paths = {
            "/auth/signup",
            "/auth/login",
            "/auth/me",
            "/catalogo/titulos",
            "/admin/exemplares",
            "/solicitacoes-emprestimo",
            "/reservas",
            "/admin/reservas/processar-expiradas",
            "/admin/exemplares/{exemplarId}/condicoes",
        }
        self.assertLessEqual(required_paths, set(paths))

        for path, path_item in paths.items():
            self.assertNotIn("delete", path_item)
            for method, operation in path_item.items():
                if method in {"get", "post", "put", "patch", "delete"}:
                    self.assertIn("responses", operation, f"{method.upper()} {path}")
                    is_public_auth = path in {"/auth/signup", "/auth/login"}
                    is_public_read = method == "get" and path.startswith("/catalogo/")
                    if not is_public_auth and not is_public_read:
                        self.assertTrue(operation.get("security"), f"{method.upper()} {path}")

        signup = paths["/auth/signup"]["post"]
        self.assertIn("perfil estudante", signup["description"])
        self.assertIn("Senha nao e normalizada", signup["description"])
        offer = paths["/admin/reservas/ofertar-proxima"]["post"]["description"]
        self.assertIn("48 horas", offer)
        self.assertIn("UTC", offer)

    def test_every_openapi_operation_has_exactly_one_xanoscript_candidate(self):
        document = json.loads(OPENAPI.read_text(encoding="utf-8"))
        operations = []
        for path, path_item in document["paths"].items():
            for method, operation in path_item.items():
                if method.lower() in {"get", "post", "put", "patch", "delete"}:
                    operations.append((method.upper(), path, operation))

        candidates = []
        for path in APIS.rglob("*.xs"):
            source = path.read_text(encoding="utf-8")
            for route, method in API_DECLARATION.findall(source):
                candidates.append((method, "/" + route, path, source))

        self.assertEqual(len(operations), 28)
        self.assertEqual(len(candidates), len(operations))

        for method, path, operation in operations:
            matches = [
                candidate
                for candidate in candidates
                if candidate[0] == method
                and normalize_path(candidate[1]) == normalize_path(path)
            ]
            self.assertEqual(
                len(matches),
                1,
                f"{method} {path} must have exactly one XS candidate",
            )
            _, _, candidate_path, source = matches[0]
            if operation.get("security"):
                self.assertIn('auth = "usuario"', source, candidate_path.name)
            if path.startswith("/admin/") or (
                path in {"/catalogo/titulos", "/catalogo/categorias"}
                and method == "POST"
            ) or (
                path.startswith("/catalogo/")
                and method == "PATCH"
            ):
                self.assertIn(
                    '$usuario.perfil == "bibliotecario"',
                    source,
                    candidate_path.name,
                )

        self.assertFalse(
            any(method in {"DELETE", "PUT"} for method, _, _ in operations)
        )
        self.assertNotIn(
            "promover",
            " ".join(path.name.lower() for path in APIS.rglob("*.xs")),
        )

    def test_candidate_inputs_cover_openapi_body_and_path_parameters(self):
        document = json.loads(OPENAPI.read_text(encoding="utf-8"))
        parameters = document.get("components", {}).get("parameters", {})
        schemas = document.get("components", {}).get("schemas", {})

        for path, path_item in document["paths"].items():
            for method, operation in path_item.items():
                if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                    continue
                matches = []
                for candidate in APIS.rglob("*.xs"):
                    source = candidate.read_text(encoding="utf-8")
                    declarations = API_DECLARATION.findall(source)
                    if any(
                        verb == method.upper()
                        and normalize_path("/" + route) == normalize_path(path)
                        for route, verb in declarations
                    ):
                        matches.append((candidate, source))
                self.assertEqual(len(matches), 1, f"{method.upper()} {path}")
                candidate, source = matches[0]
                declared = input_fields(source)

                body = operation.get("requestBody", {})
                body_schema = (
                    body.get("content", {})
                    .get("application/json", {})
                    .get("schema", {})
                )
                if "$ref" in body_schema:
                    body_schema = schemas[body_schema["$ref"].split("/")[-1]]
                self.assertLessEqual(
                    set(body_schema.get("required", [])),
                    declared,
                    candidate.name,
                )
                self.assertLessEqual(
                    set(body_schema.get("properties", {})),
                    declared,
                    candidate.name,
                )

                all_parameters = path_item.get("parameters", []) + operation.get(
                    "parameters", []
                )
                for parameter in all_parameters:
                    if "$ref" in parameter:
                        parameter = parameters[parameter["$ref"].split("/")[-1]]
                    if parameter.get("in") == "path":
                        name = re.sub(
                            r"([A-Z])", r"_\1", parameter["name"]
                        ).lower()
                        self.assertIn(name, declared, candidate.name)

    def test_openapi_preserves_loan_reservation_and_condition_rules(self):
        document = json.loads(OPENAPI.read_text(encoding="utf-8"))
        paths = document["paths"]
        loan = paths["/admin/solicitacoes/{solicitacaoId}/retirada"]["post"]
        self.assertIn("14 dias corridos", loan["description"])
        self.assertIn("atraso", paths["/solicitacoes-emprestimo"]["post"]["description"])

        reservation = paths["/admin/reservas/processar-expiradas"]["post"]["description"]
        self.assertIn("expiradas", reservation)
        self.assertIn("libera exemplares", reservation)
        self.assertIn("proximo estudante elegivel", reservation)
        self.assertIn("America/Sao_Paulo", paths["/minhas/reservas"]["get"]["responses"]["200"]["description"])

        condition = paths["/admin/exemplares/{exemplarId}/condicoes"]["post"]
        self.assertIn("dano ou perda", condition["description"])
        self.assertNotIn("cancelar", json.dumps(paths, ensure_ascii=False).lower())
        self.assertNotIn("delete", json.dumps(paths, ensure_ascii=False).lower())

    def test_circulation_candidates_encode_approved_guards_and_transitions(self):
        requests = (APIS / "emprestimos" / "solicitacoes_POST.xs").read_text(
            encoding="utf-8"
        )
        pickup = (APIS / "emprestimos" / "retirada_POST.xs").read_text(
            encoding="utf-8"
        )
        return_loan = (APIS / "emprestimos" / "devolucao_POST.xs").read_text(
            encoding="utf-8"
        )
        reservations = (APIS / "reservas" / "reservas_POST.xs").read_text(
            encoding="utf-8"
        )
        reservation_pickup = (APIS / "reservas" / "retirada_POST.xs").read_text(
            encoding="utf-8"
        )
        queue = (APIS / "reservas" / "fila_GET.xs").read_text(encoding="utf-8")
        offer = (APIS / "reservas" / "ofertar_proxima_POST.xs").read_text(
            encoding="utf-8"
        )
        expiry = (APIS / "reservas" / "processar_expiradas_POST.xs").read_text(
            encoding="utf-8"
        )
        condition = (APIS / "condicoes" / "condicoes_POST.xs").read_text(
            encoding="utf-8"
        )
        signup = (APIS / "auth" / "signup_POST.xs").read_text(encoding="utf-8")

        active_loan_sentinel = (
            "($db.emprestimo.devolvido_em == null || "
            "$db.emprestimo.devolvido_em == 0)"
        )
        self.assertEqual(2, requests.count(active_loan_sentinel))
        self.assertEqual(2, pickup.count(active_loan_sentinel))
        self.assertIn(
            "($emprestimo.devolvido_em == null || $emprestimo.devolvido_em == 0)",
            return_loan,
        )
        self.assertEqual(2, return_loan.count(active_loan_sentinel))
        self.assertEqual(2, reservations.count(active_loan_sentinel))
        self.assertEqual(2, reservation_pickup.count(active_loan_sentinel))
        self.assertEqual(2, offer.count(active_loan_sentinel))
        self.assertEqual(2, expiry.count(active_loan_sentinel))
        self.assertIn('value = "now"|to_timestamp', return_loan)
        self.assertIn('|set:"devolvido_em":$agora', return_loan)

        self.assertIn('estado == "aguardando"', requests)
        self.assertIn("vence_em < $agora", requests)
        self.assertIn('perfil : "estudante"', signup)
        self.assertNotIn("perfil", input_fields(signup))

        self.assertIn("solicitada_em: \"asc\"", pickup)
        self.assertIn("$emprestimos_ativos == 0", pickup)
        self.assertIn("$agora|add_secs_to_timestamp:1209600", pickup)

        self.assertNotRegex(offer, r"(?m)^\s*sort\s*=")
        self.assertIn(
            'value = $fila|sort:"id":"number":true|sort:"criada_em":"number":true',
            offer,
        )
        self.assertIn('value = "now"|to_timestamp', offer)
        self.assertIn("$db.emprestimo.vence_em < $agora", offer)
        self.assertNotIn('$db.emprestimo.vence_em < ("now"|to_timestamp)', offer)
        self.assertIn("$ofertada_em|add_secs_to_timestamp:172800", offer)
        self.assertIn("$atrasados == 0 && $emprestimos_do_titulo == 0", offer)
        self.assertNotRegex(queue, r"(?m)^\s*sort\s*=")
        self.assertIn(
            'value = $fila|sort:"id":"number":true|sort:"criada_em":"number":true',
            queue,
        )
        self.assertIn("response = $fila_ordenada", queue)
        self.assertNotRegex(expiry, r"(?m)^\s*sort\s*=")
        self.assertIn(
            'value = $expiradas|sort:"id":"number":true|sort:"expira_em":"number":true',
            expiry,
        )
        self.assertIn(
            'value = $fila|sort:"id":"number":true|sort:"criada_em":"number":true',
            expiry,
        )

        self.assertIn('$db.reserva.estado == "ofertada"', expiry)
        self.assertIn('data = {estado: "expirada"}', expiry)
        self.assertIn('estado: "reservado"', expiry)
        self.assertIn('$condicoes == 0', expiry)

        self.assertIn('tipo: $input.tipo', condition)
        self.assertIn('observacao: $input.observacao', condition)
        self.assertIn('data = {estado: "indisponivel"}', condition)


if __name__ == "__main__":
    unittest.main()
