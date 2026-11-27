import json

from biblioteca_mais_nova.public_data_cache import (
    _MAX_AGE_SECONDS,
    clear_public_snapshots_for_tests,
    load_public_snapshot,
    public_snapshot_path,
    save_public_snapshot,
)


def test_public_snapshot_is_persisted_and_loaded_with_fake_clock(tmp_path):
    cache_file = tmp_path / "cache.json"
    payload = [{"id": 7, "titulo": "Livro"}]

    saved = save_public_snapshot(
        "catalogo",
        payload,
        now=1_000.0,
        path=cache_file,
    )
    clear_public_snapshots_for_tests(cache_file)
    loaded = load_public_snapshot(
        "catalogo",
        now=1_000.0 + _MAX_AGE_SECONDS,
        path=cache_file,
    )

    assert saved.updated_at == 1_000.0
    assert loaded is not None
    assert loaded.updated_at == 1_000.0
    assert loaded.data == payload
    assert json.loads(cache_file.read_text(encoding="utf-8"))["version"] == 1
    assert not cache_file.with_name("cache.json.tmp").exists()


def test_public_snapshot_older_than_twenty_four_hours_is_not_used(tmp_path):
    cache_file = tmp_path / "cache.json"
    save_public_snapshot("regras", {"limite": 3}, now=100.0, path=cache_file)

    snapshot = load_public_snapshot(
        "regras",
        now=100.0 + _MAX_AGE_SECONDS + 1,
        path=cache_file,
    )

    assert snapshot is None


def test_default_snapshot_path_uses_system_temp_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "biblioteca_mais_nova.public_data_cache.tempfile.gettempdir",
        lambda: str(tmp_path),
    )

    path = public_snapshot_path()

    assert path.parent == tmp_path
