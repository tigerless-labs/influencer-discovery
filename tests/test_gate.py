import pytest

from outreach.gate import Gate, Verdict
from outreach.record import Audience, Candidate, Contact, Outcome

BAND = (5000, 200000)


@pytest.fixture
def gate():
    return Gate(BAND)


def cand(bio="AI agents and LLM tooling", **over):
    base = dict(channel="mastodon", person_key="k", display_name="X", bio=bio)
    base.update(over)
    return Candidate(**base)


def followers(n):
    return Audience(value=n, unit="followers", as_of="2026-08-07")


def with_email(c):
    c.add_contact(Contact("a@b.com", "email", "platform_field"))
    return c


def test_reachable_and_on_topic_qualifies(gate):
    assert gate.judge(with_email(cand())).outcome is Outcome.QUALIFIED


def test_no_contact_beats_every_other_verdict(gate):
    c = cand(audience=followers(8000))
    assert gate.judge(c).outcome is Outcome.NO_CONTACT


def test_a_buyer_is_rejected_even_with_a_perfect_audience(gate):
    c = with_email(cand(audience=followers(8000)))
    c.signals["is_buyer"] = True
    assert gate.judge(c).outcome is Outcome.BUYER


def test_off_topic_is_rejected(gate):
    assert gate.judge(with_email(cand(bio="sourdough and gardening"))).outcome is Outcome.OFF_TOPIC


def test_size_no_longer_rejects_in_either_direction(gate):
    for n in (400, 900_000):
        c = with_email(cand(audience=followers(n)))
        assert gate.judge(c).outcome is Outcome.QUALIFIED


def test_the_band_is_recorded_for_ordering_not_for_rejection(gate):
    inside = with_email(cand(audience=followers(50_000)))
    outside = with_email(cand(audience=followers(900_000)))
    gate.judge(inside)
    gate.judge(outside)
    assert inside.signals["in_band"] is True
    assert outside.signals["in_band"] is False


def test_band_edges_are_inclusive(gate):
    for n in BAND:
        c = with_email(cand(audience=followers(n)))
        gate.judge(c)
        assert c.signals["in_band"] is True


def test_an_unmeasured_audience_is_marked_unknown_not_false(gate):
    c = with_email(cand())
    gate.judge(c)
    assert c.signals["in_band"] is None


def test_a_non_follower_unit_is_never_measured_against_the_band(gate):
    c = with_email(cand(audience=Audience(120, "reactions", "2026-08-07")))
    verdict = gate.judge(c)
    assert verdict.band_applied is False
    assert c.signals["in_band"] is None


def test_the_verdict_carries_its_topic_evidence(gate):
    verdict = gate.judge(with_email(cand()))
    assert "llm" in verdict.reason


def test_only_a_qualified_verdict_may_reach_the_sheet(gate):
    for outcome in Outcome:
        v = Verdict(outcome=outcome, band_applied=False, reason="")
        assert v.writes_to_sheet == (outcome is Outcome.QUALIFIED)


def test_a_measured_size_below_the_floor_is_rejected():
    c = with_email(cand(audience=followers(800)))
    assert Gate(BAND, floor=1000).judge(c).outcome is Outcome.AUDIENCE_OUT_OF_BAND


def test_the_floor_is_inclusive():
    c = with_email(cand(audience=followers(1000)))
    assert Gate(BAND, floor=1000).judge(c).outcome is Outcome.QUALIFIED


def test_an_unmeasured_size_is_never_below_the_floor():
    """Channels that expose no follower count would otherwise be judged dead in a batch."""
    c = with_email(cand())
    assert Gate(BAND, floor=1000).judge(c).outcome is Outcome.QUALIFIED


def test_another_unit_is_never_measured_against_the_floor():
    c = with_email(cand(audience=Audience(12, "reactions", "2026-08-07")))
    assert Gate(BAND, floor=1000).judge(c).outcome is Outcome.QUALIFIED


def test_no_floor_leaves_the_verdict_exactly_as_before():
    c = with_email(cand(audience=followers(3)))
    assert Gate(BAND).judge(c).outcome is Outcome.QUALIFIED
