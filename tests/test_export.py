import pytest

from influencer_discovery.export import HEADERS, SUMMARY_TAB, contactable, row_for, to_workbook
from influencer_discovery.record import Audience, Candidate, Contact, Outcome
from influencer_discovery.store import Store

BAND = (5000, 200000)


def person(key, channel="blog", email=True, outcome=Outcome.QUALIFIED, followers=None, in_band=None):
    c = Candidate(
        channel=channel, person_key=key, display_name=key.title(),
        profile_url=f"https://{channel}/{key}", own_site=f"https://{key}.dev",
        audience=Audience(followers, "followers", "2026-08-07") if followers else None,
        outcome=outcome,
    )
    if email:
        c.add_contact(Contact(f"{key}@{key}.dev", "email", "site_root"))
    c.signals["topic_hits"] = ["ai"]
    c.signals["in_band"] = in_band
    return c


@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path)
    s.record(person("alice", followers=50_000, in_band=True), run_id="r")
    s.record(person("bob", channel="instagram", outcome=Outcome.OFF_TOPIC), run_id="r")
    s.record(person("carol", email=False, outcome=Outcome.NO_CONTACT), run_id="r")
    return s


def test_only_people_with_an_address_are_exported(store):
    names = {c.person_key for people in contactable(store, BAND).values() for c in people}
    assert names == {"alice", "bob"}


def test_rows_are_grouped_by_channel(store):
    assert set(contactable(store, BAND)) == {"blog", "instagram"}


def test_qualified_rows_come_first(store):
    store.record(person("dave", outcome=Outcome.BUYER), run_id="r")
    store.record(person("erin", followers=9000, in_band=True), run_id="r")
    blog = contactable(store, BAND)["blog"]
    assert blog[0].outcome is Outcome.QUALIFIED
    assert blog[-1].outcome is Outcome.BUYER


def test_a_row_carries_its_address_and_verdict():
    row = dict(zip(HEADERS, row_for(person("alice", followers=50_000, in_band=True))))
    assert row["Email"] == "alice@alice.dev"
    assert row["Email Source"] == "site_root"
    assert row["Followers"] == 50_000
    assert row["Verdict"] == "qualified"


def test_the_band_is_used_for_order_but_is_not_a_column(store):
    assert "In Band" not in HEADERS
    store.record(person("small", followers=100, in_band=False), run_id="r")
    store.record(person("right", followers=50_000, in_band=True), run_id="r")
    order = [c.person_key for c in contactable(store, BAND)["blog"]]
    assert order.index("right") < order.index("small")


def test_an_unmeasured_audience_shows_no_number():
    row = dict(zip(HEADERS, row_for(person("alice"))))
    assert row["Followers"] == ""


def test_the_workbook_has_a_summary_then_one_tab_per_channel(store):
    book = to_workbook(contactable(store, BAND))
    assert book.sheetnames == [SUMMARY_TAB, "blog", "instagram"]


def test_every_channel_tab_starts_with_the_header_row(store):
    book = to_workbook(contactable(store, BAND))
    for name in book.sheetnames[1:]:
        assert [c.value for c in book[name][1]] == HEADERS


def test_the_summary_totals_match_the_tabs(store):
    by_channel = contactable(store, BAND)
    book = to_workbook(by_channel)
    total = book[SUMMARY_TAB].max_row
    assert book[SUMMARY_TAB].cell(row=total, column=1).value == "Total"
    assert book[SUMMARY_TAB].cell(row=total, column=2).value == sum(
        len(p) for p in by_channel.values()
    )


def test_an_empty_store_still_produces_a_summary(tmp_path):
    book = to_workbook(contactable(Store(tmp_path), BAND))
    assert book.sheetnames == [SUMMARY_TAB]


def test_a_size_below_the_floor_never_reaches_the_final_table(store):
    """The verdict already rejected them; a row in the deliverable would re-admit them."""
    store.record(person("tiny", followers=800, outcome=Outcome.AUDIENCE_OUT_OF_BAND), run_id="r")
    names = {c.person_key for people in contactable(store, BAND).values() for c in people}
    assert "tiny" not in names
