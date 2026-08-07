import pytest

from outreach.gate import Gate
from outreach.record import Candidate, Contact, Outcome
from outreach.topic import hits_in, is_on_topic, note_hits


def cand(**over):
    base = dict(channel="blog", person_key="k", display_name="X")
    base.update(over)
    c = Candidate(**base)
    c.add_contact(Contact("a@b.com", "email", "site_root"))
    return c


@pytest.fixture
def gate():
    return Gate((5000, 200000))


def test_a_topic_word_is_matched_whole():
    assert hits_in("I build AI agents") == ["ai agents"]


def test_a_topic_word_inside_another_word_is_not_a_match():
    for text in ("email me", "a comfy chair", "maintain the repo", "Thailand", "said so"):
        assert hits_in(text) == []


def test_matching_is_case_insensitive():
    assert hits_in("Machine Learning") == ["machine learning"]


def test_evidence_is_the_terms_never_the_source_text():
    c = cand(bio="secret third party prose about LLM tooling")
    note_hits(c)
    assert c.signals["topic_hits"] == ["llm"]
    assert "secret third party prose" not in str(c.signals)


def test_payload_strings_count_as_evidence():
    c = cand(payload={"title": "Fine-tuning a transformer", "tag": "webdev"})
    assert "fine-tuning" in note_hits(c)


def test_off_topic_with_a_contact_is_rejected(gate):
    assert gate.judge(cand(bio="I write about gardening")).outcome is Outcome.OFF_TOPIC


def test_on_topic_without_a_follower_count_still_qualifies(gate):
    verdict = gate.judge(cand(bio="LLM evaluation notes"))
    assert verdict.outcome is Outcome.QUALIFIED
    assert verdict.band_applied is False


def test_no_contact_still_beats_the_topic_gate(gate):
    bare = Candidate(channel="blog", person_key="k", display_name="X", bio="AI agents")
    assert gate.judge(bare).outcome is Outcome.NO_CONTACT


def test_a_buyer_is_rejected_even_when_on_topic(gate):
    c = cand(bio="AI agents platform")
    c.signals["is_buyer"] = True
    assert gate.judge(c).outcome is Outcome.BUYER


def test_an_out_of_band_size_no_longer_rejects(gate):
    from outreach.record import Audience

    c = cand(bio="AI tools", audience=Audience(4_000_000, "followers", "2026-08-07"))
    verdict = gate.judge(c)
    assert verdict.outcome is Outcome.QUALIFIED
    assert c.signals["in_band"] is False


def test_ranking_puts_in_band_first_then_unknown_then_off_band(gate):
    from outreach.record import Audience

    in_band = cand(bio="ai", audience=Audience(50_000, "followers", "d"))
    unknown = cand(bio="ai")
    off_band = cand(bio="ai", audience=Audience(9_000_000, "followers", "d"))
    for c in (in_band, unknown, off_band):
        gate.judge(c)
    assert gate.rank([off_band, unknown, in_band]) == [in_band, unknown, off_band]
