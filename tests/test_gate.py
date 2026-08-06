import pytest

from outreach.gate import Gate, Verdict
from outreach.record import Audience, Candidate, Contact, Outcome


@pytest.fixture
def gate():
    return Gate(band=(5000, 100000))


def cand(**over):
    base = dict(channel="mastodon", person_key="k", display_name="X")
    base.update(over)
    return Candidate(**base)


def followers(n):
    return Audience(value=n, unit="followers", as_of="2026-08-06")


def with_email(c):
    c.add_contact(Contact("a@b.com", "email", "platform_field"))
    return c


def test_inside_the_band_passes(gate):
    c = with_email(cand(audience=followers(8000)))
    assert gate.judge(c).outcome is Outcome.QUALIFIED


def test_below_the_band_fails(gate):
    c = with_email(cand(audience=followers(400)))
    assert gate.judge(c).outcome is Outcome.AUDIENCE_OUT_OF_BAND


def test_above_the_band_fails(gate):
    c = with_email(cand(audience=followers(900000)))
    assert gate.judge(c).outcome is Outcome.AUDIENCE_OUT_OF_BAND


def test_band_edges_are_inclusive(gate):
    assert gate.judge(with_email(cand(audience=followers(5000)))).outcome is Outcome.QUALIFIED
    assert gate.judge(with_email(cand(audience=followers(100000)))).outcome is Outcome.QUALIFIED


def test_a_non_follower_unit_is_never_measured_against_the_band(gate):
    c = with_email(cand(channel="devto", audience=Audience(120, "reactions", "2026-08-06")))
    v = gate.judge(c)
    assert v.outcome is not Outcome.AUDIENCE_OUT_OF_BAND
    assert v.band_applied is False


def test_without_a_number_the_sponsor_signal_carries_it(gate):
    c = with_email(cand(channel="podcast"))
    c.signals["sponsor_page"] = True
    v = gate.judge(c)
    assert v.outcome is Outcome.QUALIFIED
    assert v.band_applied is False


def test_without_a_number_and_without_a_sponsor_signal_it_fails(gate):
    c = with_email(cand(channel="podcast"))
    c.signals["sponsor_page"] = False
    assert gate.judge(c).outcome is Outcome.AUDIENCE_UNVERIFIED


def test_no_contact_beats_every_other_verdict(gate):
    c = cand(audience=followers(8000))
    c.signals["sponsor_page"] = True
    assert gate.judge(c).outcome is Outcome.NO_CONTACT


def test_a_buyer_is_rejected_even_with_a_perfect_audience(gate):
    c = with_email(cand(audience=followers(8000)))
    c.signals["is_buyer"] = True
    assert gate.judge(c).outcome is Outcome.BUYER


def test_only_a_qualified_verdict_may_reach_the_sheet(gate):
    for outcome in Outcome:
        v = Verdict(outcome=outcome, band_applied=False, reason="")
        assert v.writes_to_sheet == (outcome is Outcome.QUALIFIED)


def test_an_email_alone_is_not_enough_without_a_signal(gate):
    c = with_email(cand(channel="podcast"))
    assert gate.judge(c).outcome is Outcome.AUDIENCE_UNVERIFIED
