from copy import deepcopy

from scripts.demo_api import DemoData, seed_demo_data
from scripts.demo_seed_data import CATEGORY_NAMES, DEMO_USERS, SEED_TITLES
from scripts.seed_xano_demo import main as seed_xano_main, seed_catalog


def _snapshot(data: DemoData) -> tuple[object, ...]:
    return deepcopy(
        (
            data.categories,
            data.titles,
            data.title_categories,
            data.copies,
            data.students,
            data.users,
        )
    )


def test_demo_seed_has_required_books_categories_copies_and_roles() -> None:
    data = DemoData()

    assert len(SEED_TITLES) == 30
    assert len(data.categories) >= 6
    assert {item["nome"] for item in data.categories} >= set(CATEGORY_NAMES)
    assert len(data.titles) == 30
    assert len({item["titulo"] for item in data.titles}) == 30
    assert all(
        any(link["titulo_id"] == title["id"] for link in data.title_categories)
        for title in data.titles
    )
    copy_counts = {
        len(
            [
                copy
                for copy in data.copies
                if copy["titulo_id"] == title["id"]
            ]
        )
        for title in data.titles
    }
    assert len(copy_counts) > 1
    assert all(title["descricao"] is None for title in data.titles)
    assert {user["perfil"] for user in DEMO_USERS} == {
        "estudante",
        "bibliotecario",
        "admin",
    }
    assert all(user["email"].endswith("@example.invalid") for user in DEMO_USERS)
    assert {user["perfil"] for user in data.users.values()} == {
        "estudante",
        "bibliotecario",
        "admin",
    }


def test_demo_seed_is_idempotent() -> None:
    data = DemoData()
    before = _snapshot(data)

    seed_demo_data(data)
    seed_demo_data(data)

    assert _snapshot(data) == before


def test_xano_seed_defaults_to_preview_without_network(
    monkeypatch, capsys
) -> None:
    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("A prévia não deve fazer chamadas.")

    monkeypatch.setattr("scripts.seed_xano_demo.request_json", fail_if_called)

    assert seed_xano_main([]) == 0
    assert "nenhuma chamada foi realizada" in capsys.readouterr().out


def test_xano_seed_is_idempotent_with_mocked_transport() -> None:
    categories: list[dict[str, object]] = []
    catalog: list[dict[str, object]] = []
    next_id = 1

    def fake_request(method, path, _base_url, _token, body):
        nonlocal next_id
        if method == "GET" and path == "/catalogo/categorias":
            return deepcopy(categories)
        if method == "GET" and path == "/admin/acervo":
            return deepcopy(catalog)
        if method == "POST" and path == "/catalogo/categorias":
            record = {"id": next_id, "nome": body["nome"]}
            next_id += 1
            categories.append(record)
            return deepcopy(record)
        if method == "POST" and path == "/catalogo/titulos":
            title = {"id": next_id, **body}
            next_id += 1
            catalog.append(
                {"titulo": title, "categorias": [], "exemplares": []}
            )
            return deepcopy(title)
        if method == "POST" and path.startswith("/admin/titulos/"):
            title_id = int(path.split("/")[3])
            catalog_entry = next(
                entry for entry in catalog if entry["titulo"]["id"] == title_id
            )
            catalog_entry["categorias"].append(
                {
                    "categoria_id": body["categoria_id"],
                    "titulo_id": title_id,
                }
            )
            return {"id": next_id}
        if method == "POST" and path == "/admin/exemplares":
            copy = {"id": next_id, "titulo_id": body["titulo_id"]}
            next_id += 1
            entry = next(
                item
                for item in catalog
                if item["titulo"]["id"] == body["titulo_id"]
            )
            entry["exemplares"].append(copy)
            return deepcopy(copy)
        raise AssertionError(f"Chamada inesperada: {method} {path}")

    first_run = seed_catalog("https://demo.invalid", "", fake_request)
    second_run = seed_catalog("https://demo.invalid", "", fake_request)

    assert first_run["categorias"] == 7
    assert first_run["titulos"] == 30
    assert all(value == 0 for value in second_run.values())
