import pytest

from influencer_discovery.record import Audience, Candidate, Contact, Outcome


def make(**over):
    base = dict(channel="podcast", person_key="show-abc", display_name="Show ABC")
    base.update(over)
    return Candidate(**base)


def test_audience_carries_its_unit():
    a = Audience(value=8200, unit="followers", as_of="2026-08-06")
    assert a.unit == "followers"


def test_audience_of_different_units_refuses_comparison():
    followers = Audience(value=8200, unit="followers", as_of="2026-08-06")
    reactions = Audience(value=8200, unit="reactions", as_of="2026-08-06")
    with pytest.raises(TypeError):
        followers.compare(reactions)


def test_audience_of_same_unit_compares():
    small = Audience(value=100, unit="followers", as_of="2026-08-06")
    large = Audience(value=900, unit="followers", as_of="2026-08-06")
    assert small.compare(large) < 0


def test_contact_without_source_is_rejected():
    with pytest.raises(ValueError):
        Contact(value="a@b.com", kind="email", source="")


def test_contact_rejects_unknown_kind():
    with pytest.raises(ValueError):
        Contact(value="a@b.com", kind="carrier-pigeon", source="feed_owner")


def test_absent_and_unchecked_are_distinguishable():
    unchecked = make()
    checked_empty = make()
    checked_empty.mark_checked("own_site")
    assert unchecked.was_checked("own_site") is False
    assert checked_empty.was_checked("own_site") is True
    assert checked_empty.own_site is None


def test_record_accumulates_without_changing_type():
    c = make()
    c.own_site = "https://example.com"
    c.add_contact(Contact("a@b.com", "email", "feed_owner"))
    c.outcome = Outcome.QUALIFIED
    assert isinstance(c, Candidate)
    assert c.outcome is Outcome.QUALIFIED


def test_dead_end_still_carries_a_full_record():
    c = make()
    c.outcome = Outcome.NO_CONTACT
    row = c.to_row()
    assert row["person_key"] == "show-abc"
    assert row["outcome"] == "no_contact"


def test_payload_survives_roundtrip_untouched():
    weird = {"feedUrl": "https://x/f.xml", "nested": {"a": [1, 2]}}
    c = make(payload=weird)
    assert Candidate.from_row(c.to_row()).payload == weird


def test_dedup_key_is_person_and_channel():
    assert make().dedup_key == ("show-abc", "podcast")


def test_display_name_is_not_part_of_the_key():
    a = make(display_name="One")
    b = make(display_name="Two")
    assert a.dedup_key == b.dedup_key


def test_fetch_failure_is_not_an_outcome_value():
    assert not any(o.value == "fetch_failed" for o in Outcome)
