import json

import pytest

from outreach.fetch import RawStore


@pytest.fixture
def raw(tmp_path):
    return RawStore(tmp_path / "raw")


def test_the_same_address_is_stored_once_across_runs(raw):
    raw.put("https://a.dev/x", "first", run_id="r1")
    raw.put("https://a.dev/x", "first", run_id="r2")
    assert len(list(raw.blobs())) == 1


def test_each_run_keeps_its_own_list_of_what_it_touched(raw):
    raw.put("https://a.dev/x", "b", run_id="r1")
    raw.put("https://b.dev/y", "b", run_id="r2")
    assert raw.digests_for("r1") != raw.digests_for("r2")
    assert len(raw.digests_for("r1")) == 1


def test_a_run_that_revisits_an_address_lists_it_once(raw):
    raw.put("https://a.dev/x", "b", run_id="r1")
    raw.put("https://a.dev/x", "b", run_id="r1")
    assert len(raw.digests_for("r1")) == 1


def test_a_body_reads_back_by_address(raw):
    raw.put("https://a.dev/x", "hello", run_id="r1")
    assert raw.get("https://a.dev/x") == "hello"


def test_an_unknown_address_reads_back_as_nothing(raw):
    assert raw.get("https://never.dev") is None


def test_the_first_body_wins_so_history_is_not_rewritten(raw):
    raw.put("https://a.dev/x", "original", run_id="r1")
    raw.put("https://a.dev/x", "changed", run_id="r2")
    assert raw.get("https://a.dev/x") == "original"


def test_a_corrupt_blob_reads_back_as_nothing(raw):
    raw.put("https://a.dev/x", "hi", run_id="r1")
    next(iter(raw.blobs())).write_text("{broken", encoding="utf-8")
    assert raw.get("https://a.dev/x") is None


def test_migration_folds_per_run_directories_into_blobs(tmp_path):
    root = tmp_path / "raw"
    for run in ("r1", "r2"):
        directory = root / run
        directory.mkdir(parents=True)
        (directory / "deadbeefdeadbeef.json").write_text(
            json.dumps({"url": "https://a.dev/x", "body": "same"}), encoding="utf-8"
        )
    moved = RawStore(root).migrate()
    store = RawStore(root)
    assert moved == 2
    assert len(list(store.blobs())) == 1
    assert store.get("https://a.dev/x") == "same"
    assert store.digests_for("r1") == store.digests_for("r2")


def test_migration_leaves_nothing_behind(tmp_path):
    root = tmp_path / "raw"
    (root / "r1").mkdir(parents=True)
    (root / "r1" / "aaaa.json").write_text(
        json.dumps({"url": "https://a.dev", "body": "x"}), encoding="utf-8"
    )
    RawStore(root).migrate()
    assert not (root / "r1").exists()


def test_migration_is_safe_to_run_twice(tmp_path):
    root = tmp_path / "raw"
    (root / "r1").mkdir(parents=True)
    (root / "r1" / "aaaa.json").write_text(
        json.dumps({"url": "https://a.dev", "body": "x"}), encoding="utf-8"
    )
    RawStore(root).migrate()
    assert RawStore(root).migrate() == 0
    assert RawStore(root).get("https://a.dev") == "x"


def test_a_replay_can_be_pinned_to_one_run(tmp_path, monkeypatch):
    from outreach import fetch as fetch_module

    monkeypatch.setattr(fetch_module, "state_dir", lambda: tmp_path)
    store = fetch_module.RawStore()
    store.put("https://a.dev", "from r1", run_id="r1")
    store.put("https://b.dev", "from r2", run_id="r2")

    only_r1 = fetch_module.ReplayFetcher(run_ids=["r1"])
    assert only_r1.try_get("https://a.dev") == "from r1"
    assert only_r1.try_get("https://b.dev") is None
    assert fetch_module.ReplayFetcher().try_get("https://b.dev") == "from r2"
