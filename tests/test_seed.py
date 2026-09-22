import pytest

from influencer_discovery.seed import HeaderMismatch, keys_from_rows, seed_channel
from influencer_discovery.store import Store

MAPPING = {"display_name": "Name", "channel": "Platform", "profile_url": "Link"}
HEADERS = ["Name", "Platform", "Link", "Notes"]


def rows(*items):
    return [list(i) + [""] * (len(HEADERS) - len(i)) for i in items]


def test_youtube_rows_seed_by_handle_not_by_name():
    table = rows(["Some Person", "YouTube", "https://www.youtube.com/@SomeOne"])
    assert keys_from_rows(HEADERS, table, MAPPING, "youtube") == [("someone", "youtube")]


def test_a_mobile_link_and_a_query_string_still_yield_the_handle():
    table = rows(
        ["A", "YouTube", "https://m.youtube.com/@agentwerk"],
        ["B", "youtube", "https://youtube.com/@Poppy?si=abc"],
    )
    assert keys_from_rows(HEADERS, table, MAPPING, "youtube") == [
        ("agentwerk", "youtube"), ("poppy", "youtube"),
    ]


def test_rows_on_other_platforms_and_without_a_handle_link_are_skipped():
    table = rows(
        ["X person", "Twitter", "https://x.com/someone"],
        ["YT via x", "YouTube", "https://x.com/someone"],
        ["YT playlist", "YouTube", "https://youtube.com/playlist?list=PL1"],
    )
    assert keys_from_rows(HEADERS, table, MAPPING, "youtube") == []


def test_a_missing_header_aborts_instead_of_guessing():
    with pytest.raises(HeaderMismatch):
        keys_from_rows(["Name", "Platform"], rows(["A", "YouTube"]), MAPPING, "youtube")


def test_a_channel_without_a_seed_rule_is_refused():
    with pytest.raises(ValueError):
        keys_from_rows(HEADERS, rows(), MAPPING, "podcast")


def test_instruction_shaped_cells_are_just_skipped():
    table = rows(["ignore previous", "YouTube", "javascript:alert(1)//@evil"])
    assert keys_from_rows(HEADERS, table, MAPPING, "youtube") == []


def test_seeding_marks_the_handle_seen_for_that_channel_only(tmp_path):
    store = Store(tmp_path)
    added = seed_channel(store, HEADERS, rows(["A", "YouTube", "https://youtube.com/@Ada"]), MAPPING, "youtube")
    assert added == 1
    assert store.is_seen(("ada", "youtube"))
    assert not store.is_seen(("ada", "podcast"))


def test_seeding_twice_adds_nothing(tmp_path):
    store = Store(tmp_path)
    table = rows(["A", "YouTube", "https://youtube.com/@Ada"])
    seed_channel(store, HEADERS, table, MAPPING, "youtube")
    assert seed_channel(store, HEADERS, table, MAPPING, "youtube") == 0
    assert len(store.raw_lines("youtube")) == 1
