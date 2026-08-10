import tomllib

import pytest

from outreach import channels as channel_registry
from outreach import run as run_module
from outreach.channels.base import Channel
from outreach.paths import repo_config_dir
from outreach.record import Audience, Candidate, Contact, Outcome
from outreach.run import Run, load_config, select, tier_of
from outreach.store import Store

BAND = (5000, 200000)


def person(key, followers=None, email=True, buyer=False, on_topic=True):
    c = Candidate(
        channel="fake",
        person_key=key,
        display_name=key,
        bio="writes about AI agents and LLM tooling" if on_topic else "sourdough and gardening",
        audience=Audience(followers, "followers", "2026-08-07") if followers else None,
    )
    if email:
        c.add_contact(Contact(f"{key}@{key}.dev", "email", "platform_field"))
    if buyer:
        c.signals["is_buyer"] = True
    return c


class FakePool(Channel):
    name = "fake"
    form = "search"

    def __init__(self, people, form="search"):
        self.people = people
        self.form = form
        self.asked_for = None

    def discover(self, limit):
        self.asked_for = limit
        return self.people[:limit]


@pytest.fixture
def runner(tmp_path, monkeypatch):
    def make(adapter, per_channel=3, store=None):
        monkeypatch.setattr(channel_registry, "build", lambda *a, **k: adapter)
        monkeypatch.setattr(run_module.SecondHop, "walk", lambda self, candidate: None)
        r = Run("test", per_channel, BAND, "test", store=store or Store(tmp_path))
        r.channel("fake", {})
        return r.report.channels["fake"]

    return make


def test_the_target_counts_qualified_rows_not_crawled_ones(runner):
    duds = [person(f"dud{i}", on_topic=False) for i in range(20)]
    good = [person(f"good{i}", followers=9000) for i in range(3)]
    block = runner(FakePool(duds + good), per_channel=3)
    assert len(block["qualified"]) == 3
    assert block["crawled"] > 3


def test_it_stops_the_moment_the_target_is_met(runner):
    good = [person(f"good{i}", followers=9000) for i in range(10)]
    block = runner(FakePool(good), per_channel=3)
    assert len(block["qualified"]) == 3
    assert block["crawled"] == 3
    assert block["stop"] == "quota met"


def test_a_dry_search_pool_stops_as_no_new_rather_than_met(runner):
    block = runner(FakePool([person(f"dud{i}", on_topic=False) for i in range(5)]), per_channel=3)
    assert len(block["qualified"]) == 0
    assert block["stop"] == "no new results"


def test_a_dry_directory_pool_stops_as_exhausted(runner):
    pool = FakePool([person(f"dud{i}", on_topic=False) for i in range(5)], form="directory")
    block = runner(pool, per_channel=3)
    assert block["stop"] == "paged to the end"


def test_a_shortfall_says_whether_people_or_evidence_ran_out(runner):
    thin = runner(FakePool([person("only", on_topic=False)]), per_channel=3)
    assert thin["shortfall"] == "too few candidates"

    plenty = runner(FakePool([person(f"d{i}", on_topic=False) for i in range(30)]), per_channel=3)
    assert plenty["shortfall"] == "stuck at the gate"


def test_a_met_target_has_no_shortfall(runner):
    block = runner(FakePool([person(f"g{i}", followers=9000) for i in range(5)]), per_channel=3)
    assert block["shortfall"] is None


def test_people_already_in_the_log_do_not_consume_the_target(runner, tmp_path):
    store = Store(tmp_path)
    seen = person("known", followers=9000)
    seen.channel = "fake"
    store.record(seen, run_id="earlier")

    pool = [seen, person("fresh1", followers=9000), person("fresh2", followers=9000)]
    block = runner(FakePool(pool), per_channel=2, store=store)
    assert {c.person_key for c in block["qualified"]} == {"fresh1", "fresh2"}


def test_the_pool_asked_for_is_a_multiple_of_the_target(runner):
    pool = FakePool([person(f"d{i}", on_topic=False) for i in range(200)])
    runner(pool, per_channel=3)
    assert pool.asked_for > 3


def test_a_buyer_never_counts_toward_the_target(runner):
    pool = [person(f"b{i}", followers=9000, buyer=True) for i in range(5)]
    block = runner(FakePool(pool), per_channel=3)
    assert len(block["qualified"]) == 0
    assert block["outcomes"][Outcome.BUYER] == 5


CONFIG = load_config("channels.toml")


def test_every_channel_points_at_a_methodology_document():
    root = repo_config_dir().parent / "skills/outreach/reference/methodology"
    for name, entry in CONFIG.items():
        if not isinstance(entry, dict):
            continue
        assert "methodology" in entry, f"{name} has no methodology pointer"
        assert (root / entry["methodology"]).exists(), f"{name} points at a missing document"


def test_the_tier_comes_from_the_pointer_not_from_a_second_copy():
    assert tier_of({"methodology": "1-social/mastodon.md"}) == 1
    assert tier_of({"methodology": "2-blog-platform/dev-to.md"}) == 2
    for entry in CONFIG.values():
        if isinstance(entry, dict):
            assert "tier" not in entry


def test_selecting_tiers_keeps_only_those_tiers():
    picked = select(CONFIG, tiers="1,2")
    assert picked
    assert all(tier_of(CONFIG[n]) in {1, 2} for n in picked)
    assert set(picked) < {n for n, v in CONFIG.items() if isinstance(v, dict)}


def test_an_unknown_channel_name_is_dropped_not_guessed():
    assert select(CONFIG, names="mastodon,not-a-channel") == ["mastodon"]


def test_the_first_two_tiers_leave_the_personal_site_channels_out():
    picked = select(CONFIG, tiers="1,2")
    assert {"podcast", "newsletter", "blog"}.isdisjoint(picked)


def test_the_config_parses_as_toml():
    tomllib.loads((repo_config_dir() / "channels.toml").read_text(encoding="utf-8"))


def rejudged(tmp_path, candidate):
    store = Store(tmp_path)
    candidate.outcome = Outcome.QUALIFIED
    store.record(candidate, run_id="before")
    run_module.rejudge("fix", BAND, store=store)
    return next(c for c in store.people() if c.person_key == candidate.person_key)


def test_a_platform_address_stored_as_qualified_is_demoted(tmp_path):
    c = person("staff", followers=9000, email=False)
    c.add_contact(Contact("partners@dev.to", "email", "sponsor_page"))
    fixed = rejudged(tmp_path, c)
    assert fixed.contacts == []
    assert fixed.outcome is Outcome.NO_CONTACT


def test_a_still_valid_row_keeps_its_verdict(tmp_path):
    fixed = rejudged(tmp_path, person("real", followers=9000))
    assert fixed.outcome is Outcome.QUALIFIED
    assert fixed.email == "real@real.dev"


def test_rejudging_reports_only_what_it_changed(tmp_path):
    store = Store(tmp_path)
    good = person("good", followers=9000)
    good.outcome = Outcome.QUALIFIED
    store.record(good, run_id="before")
    run_module.rejudge("fix", BAND, store=store)
    assert run_module.rejudge("again", BAND, store=store) == []


def test_the_replay_fetcher_serves_disk_and_never_the_network(tmp_path, monkeypatch):
    from outreach import fetch as fetch_module

    monkeypatch.setattr(fetch_module, "state_dir", lambda: tmp_path)
    url = "https://janesblog.dev"
    fetch_module.RawStore().put(url, "<p>hi</p>", run_id="earlier")

    replay = fetch_module.ReplayFetcher()
    assert replay.try_get(url) == "<p>hi</p>"
    assert replay.try_get("https://never-fetched.example") is None
    assert not hasattr(replay, "get")


def test_a_stale_buyer_call_is_cleared_before_the_page_is_read_again(tmp_path, monkeypatch):
    store = Store(tmp_path)
    c = person("blogger", followers=9000)
    c.own_site = "https://janesblog.dev"
    c.signals["is_buyer"] = True
    c.signals["buyer_reason"] = "stale"
    c.outcome = Outcome.BUYER
    store.record(c, run_id="before")

    monkeypatch.setattr(run_module.SecondHop, "walk", lambda self, candidate: candidate)
    run_module.rejudge("fix", BAND, store=store, replay=True)
    fixed = next(x for x in store.people() if x.person_key == "blogger")
    assert fixed.outcome is Outcome.QUALIFIED
    assert "is_buyer" not in fixed.signals


def test_rejudging_persists_refreshed_evidence_behind_an_unchanged_verdict(tmp_path):
    from outreach.run import rejudge

    store = Store(tmp_path)
    stale = person("keeper", followers=9000)
    stale.outcome = Outcome.QUALIFIED
    stale.signals["verdict_reason"] = "sponsorship page on own site"
    store.record(stale, run_id="old")

    changed = rejudge("fresh", BAND, store=store)

    assert [c.person_key for c in changed] == ["keeper"]
    kept = next(iter(store.people()))
    assert kept.outcome is Outcome.QUALIFIED
    assert kept.signals["topic_hits"]
    assert kept.signals["verdict_reason"] != "sponsorship page on own site"


def test_rejudging_leaves_an_already_current_row_alone(tmp_path):
    from outreach.run import rejudge

    store = Store(tmp_path)
    current = person("settled", followers=9000)
    store.record(current, run_id="r1")
    rejudge("r2", BAND, store=store)
    before = len(store.raw_lines("fake"))
    assert rejudge("r3", BAND, store=store) == []
    assert len(store.raw_lines("fake")) == before


def test_people_past_the_target_are_still_logged(runner, tmp_path):
    store = Store(tmp_path)
    pool = FakePool([person(f"p{i}", followers=9000) for i in range(8)])
    runner(pool, per_channel=3, store=store)
    rows = {r.person_key for r in store.people("fake")}
    assert len(rows) == 8


def test_parked_people_carry_no_verdict(runner, tmp_path):
    store = Store(tmp_path)
    runner(FakePool([person(f"p{i}", followers=9000) for i in range(6)]), per_channel=2, store=store)
    parked = [r for r in store.people("fake") if r.signals.get("pending_judgement")]
    assert len(parked) == 4
    assert all(r.outcome is None for r in parked)


def test_a_parked_person_is_not_rediscovered(runner, tmp_path):
    store = Store(tmp_path)
    runner(FakePool([person(f"p{i}", followers=9000) for i in range(6)]), per_channel=2, store=store)
    assert store.is_seen(("p5", "fake"))


def with_site(c):
    c.own_site = f"https://{c.person_key}.dev"
    return c


def test_someone_below_the_floor_is_never_walked(tmp_path, monkeypatch):
    """Below the floor is a decision not to spend, not just a decision not to write."""
    walked = []
    monkeypatch.setattr(channel_registry, "build",
                        lambda *a, **k: FakePool([with_site(person("tiny", followers=800, email=False))]))
    monkeypatch.setattr(run_module.SecondHop, "walk", lambda self, c: walked.append(c.person_key))
    r = Run("test", 3, BAND, "test", store=Store(tmp_path), floor=1000)
    r.channel("fake", {})
    assert walked == []


def test_someone_above_the_floor_is_still_walked(tmp_path, monkeypatch):
    walked = []
    monkeypatch.setattr(channel_registry, "build",
                        lambda *a, **k: FakePool([with_site(person("big", followers=9000, email=False))]))
    monkeypatch.setattr(run_module.SecondHop, "walk", lambda self, c: walked.append(c.person_key))
    r = Run("test", 3, BAND, "test", store=Store(tmp_path), floor=1000)
    r.channel("fake", {})
    assert walked == ["big"]


def test_rejudging_drops_the_evidence_it_is_about_to_recompute(tmp_path, monkeypatch):
    """Stored hits came from the old rule; keeping them would re-confirm the verdict being retested."""
    store = Store(tmp_path)
    c = person("stale", followers=9000, on_topic=False)
    c.signals["topic_hits"] = ["ai agents"]
    c.outcome = Outcome.QUALIFIED
    store.record(c, run_id="old")
    monkeypatch.setattr(run_module.SecondHop, "walk", lambda self, candidate: None)
    run_module.rejudge("re", BAND, store=store)
    after = next(p for p in store.people() if p.person_key == "stale")
    assert after.outcome is Outcome.OFF_TOPIC


def test_one_poisonous_candidate_does_not_take_the_channel_down(tmp_path, monkeypatch):
    """A channel that dies mid-judging discards everyone already judged in that pass."""
    def explode(self, candidate):
        if candidate.person_key == "bad":
            raise ValueError("Invalid IPv6 URL")

    monkeypatch.setattr(channel_registry, "build", lambda *a, **k: FakePool(
        [with_site(person("first", followers=9000, email=False)),
         with_site(person("bad", followers=9000, email=False)),
         with_site(person("third", followers=9000, email=False))]))
    monkeypatch.setattr(run_module.SecondHop, "walk", explode)
    store = Store(tmp_path)
    r = Run("test", 5, BAND, "test", store=store)
    r.channel("fake", {})
    judged = {p.person_key for p in store.people()}
    assert {"first", "third"} <= judged
