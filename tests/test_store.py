import pytest

from influencer_discovery.record import Candidate, Outcome
from influencer_discovery.store import Store


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path)


def cand(channel="podcast", key="show-abc", **over):
    return Candidate(channel=channel, person_key=key, display_name="X", **over)


def test_writing_the_same_key_twice_keeps_one(store):
    store.record(cand(), run_id="r1")
    store.record(cand(), run_id="r2")
    assert len(list(store.people())) == 1


def test_seen_survives_a_fresh_reader(store, tmp_path):
    store.record(cand(), run_id="r1")
    assert Store(tmp_path).is_seen(("show-abc", "podcast"))


def test_same_person_on_another_channel_is_not_seen(store):
    store.record(cand(channel="podcast"), run_id="r1")
    assert not store.is_seen(("show-abc", "mastodon"))


def test_channels_are_separate_files_but_one_logical_table(store, tmp_path):
    store.record(cand(channel="podcast", key="a"), run_id="r1")
    store.record(cand(channel="devto", key="b"), run_id="r1")
    names = {p.name for p in (tmp_path / "seen").glob("*.jsonl")}
    assert names == {"podcast.jsonl", "devto.jsonl"}
    assert len(list(Store(tmp_path).people())) == 2


def test_a_failed_fetch_leaves_no_record(store):
    store.record_failure("https://x/y", "timeout", run_id="r1")
    assert list(store.people()) == []
    assert store.failures()[0]["reason"] == "timeout"


def test_sites_live_in_their_own_keyspace(store):
    store.record_site("example.com", outcome="no_contact", run_id="r1")
    assert store.is_site_seen("example.com")
    assert not store.is_seen(("example.com", "podcast"))
    assert list(store.people()) == []


def test_a_site_key_never_merges_two_people(store):
    store.record(cand(channel="podcast", key="host-one", own_site="https://show.fm"), run_id="r1")
    store.record(cand(channel="podcast", key="host-two", own_site="https://show.fm"), run_id="r1")
    assert len(list(store.people())) == 2


def test_records_are_append_only(store):
    store.record(cand(outcome=Outcome.NO_CONTACT), run_id="r1")
    before = store.raw_lines("podcast")
    store.record(cand(outcome=Outcome.QUALIFIED), run_id="r2")
    after = store.raw_lines("podcast")
    assert after[0] == before[0]
    assert len(after) == 2


def test_latest_wins_when_reading_back(store):
    store.record(cand(outcome=Outcome.NO_CONTACT), run_id="r1")
    store.record(cand(outcome=Outcome.QUALIFIED), run_id="r2")
    assert next(iter(store.people())).outcome is Outcome.QUALIFIED


def test_seeding_from_the_sheet_marks_people_seen(store):
    store.seed([("Ada Lovelace", "Podcast"), ("Grace Hopper", "Newsletter")])
    assert store.is_seen(("ada lovelace", "podcast"))
    assert store.is_seen(("grace hopper", "newsletter"))


def test_a_corrupt_line_does_not_kill_the_reader(store, tmp_path):
    store.record(cand(), run_id="r1")
    with (tmp_path / "seen" / "podcast.jsonl").open("a") as f:
        f.write("{not json\n")
    assert len(list(Store(tmp_path).people())) == 1


def test_walking_the_same_site_twice_leaves_one_line(store):
    store.record_site("example.com", outcome="no_contact", run_id="r1")
    store.record_site("example.com", outcome="found", run_id="r2")
    assert len(store.raw_site_lines()) == 1


def test_two_different_sites_both_land(store):
    store.record_site("a.com", outcome="found", run_id="r1")
    store.record_site("b.com", outcome="found", run_id="r1")
    assert store.seen_sites() == {"a.com", "b.com"}


def test_a_fresh_reader_still_skips_a_recorded_site(store, tmp_path):
    store.record_site("example.com", outcome="found", run_id="r1")
    other = Store(tmp_path)
    other.record_site("example.com", outcome="found", run_id="r2")
    assert len(other.raw_site_lines()) == 1


def test_compacting_collapses_an_old_duplicated_log(store):
    for _ in range(4):
        store._append(store.sites_file, {"domain": "dup.com", "outcome": "found"})
    store._sites = None
    before, after = store.compact_sites()
    assert (before, after) == (4, 1)
    assert store.seen_sites() == {"dup.com"}


def test_compacting_an_already_clean_log_changes_nothing(store):
    store.record_site("a.com", outcome="found", run_id="r1")
    assert store.compact_sites() == (1, 1)
