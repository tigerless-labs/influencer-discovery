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


def test_a_new_blob_is_written_compressed(raw):
    blob = raw.put("https://a.dev", "x" * 5000, run_id="r1")
    assert blob.suffix == ".gz"
    assert blob.stat().st_size < 5000


def test_a_compressed_blob_reads_back_intact(raw):
    body = "<html>" + "hello " * 2000 + "</html>"
    raw.put("https://a.dev", body, run_id="r1")
    assert raw.get("https://a.dev") == body


def test_packing_converts_a_plain_blob_and_keeps_its_body(raw):
    raw.blob_dir.mkdir(parents=True, exist_ok=True)
    digest = raw.digest_of("https://plain.dev")
    (raw.blob_dir / f"{digest}.json").write_text(
        json.dumps({"url": "https://plain.dev", "body": "kept"}), encoding="utf-8"
    )
    assert raw.pack() == 1
    assert raw.get("https://plain.dev") == "kept"
    assert not (raw.blob_dir / f"{digest}.json").exists()


def test_packing_twice_is_a_no_op(raw):
    raw.put("https://a.dev", "body", run_id="r1")
    assert raw.pack() == 0


def test_a_plain_blob_is_still_readable_before_packing(raw):
    raw.blob_dir.mkdir(parents=True, exist_ok=True)
    digest = raw.digest_of("https://plain.dev")
    (raw.blob_dir / f"{digest}.json").write_text(
        json.dumps({"url": "https://plain.dev", "body": "legacy"}), encoding="utf-8"
    )
    assert raw.get("https://plain.dev") == "legacy"


def test_a_second_visit_is_served_from_disk_without_a_request(tmp_path, monkeypatch):
    from outreach import fetch as fetch_module

    monkeypatch.setattr(fetch_module, "state_dir", lambda: tmp_path)
    fetcher = fetch_module.Fetcher("run1")
    fetcher.raw.put("https://shared.dev", "<p>page</p>", run_id="earlier")

    def explode(*a, **k):
        raise AssertionError("the network must not be touched for a reused page")

    monkeypatch.setattr(fetch_module.urllib.request, "urlopen", explode)
    assert fetcher.try_get("https://shared.dev", reuse=True) == "<p>page</p>"
    assert fetcher.reused == 1


def test_reuse_still_credits_the_current_run(tmp_path, monkeypatch):
    from outreach import fetch as fetch_module

    monkeypatch.setattr(fetch_module, "state_dir", lambda: tmp_path)
    fetcher = fetch_module.Fetcher("run2")
    fetcher.raw.put("https://shared.dev", "body", run_id="earlier")
    fetcher.try_get("https://shared.dev", reuse=True)
    assert fetcher.raw.digest_of("https://shared.dev") in fetcher.raw.digests_for("run2")


def test_without_reuse_a_known_page_is_still_fetched(tmp_path, monkeypatch):
    from outreach import fetch as fetch_module

    monkeypatch.setattr(fetch_module, "state_dir", lambda: tmp_path)
    fetcher = fetch_module.Fetcher("run3")
    fetcher.raw.put("https://shared.dev", "old", run_id="earlier")
    calls = []
    monkeypatch.setattr(
        fetch_module.urllib.request, "urlopen",
        lambda *a, **k: calls.append(1) or (_ for _ in ()).throw(OSError("no network")),
    )
    assert fetcher.try_get("https://shared.dev") is None
    assert calls == [1]


def test_the_replay_fetcher_accepts_the_same_call_as_the_real_one(tmp_path):
    """The walk calls it with reuse/persist; a narrower signature makes replay die on the first site."""
    import inspect

    from outreach.fetch import Fetcher, ReplayFetcher

    for name in ("try_get", "try_json"):
        real = set(inspect.signature(getattr(Fetcher, name)).parameters)
        replay = set(inspect.signature(getattr(ReplayFetcher, name)).parameters)
        assert real <= replay, f"{name}: replay is missing {real - replay}"
