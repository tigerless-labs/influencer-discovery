import pytest

from outreach.record import Candidate, Contact
from outreach.sheet import HeaderMismatch, TargetSheet

HEADERS = ["Name", "Platform", "Link", "Contact", "Contact Type", "Status"]

MAPPING = {
    "display_name": "Name",
    "channel": "Platform",
    "profile_url": "Link",
    "contact": "Contact",
    "contact_kind": "Contact Type",
    "status": "Status",
}


class FakeApi:
    def __init__(self, headers, rows=0):
        self.headers = headers
        self.rows = rows
        self.appended = []

    def read_headers(self, tab):
        return self.headers

    def append(self, tab, values):
        self.appended.extend(values)


def qualified():
    c = Candidate(channel="podcast", person_key="k", display_name="Ada", profile_url="https://p")
    c.add_contact(Contact("a@b.com", "email", "feed_owner"))
    return c


def test_a_matching_header_lets_the_write_through():
    api = FakeApi(HEADERS)
    TargetSheet(api, "Target List", MAPPING).append([qualified()])
    assert len(api.appended) == 1


def test_a_renamed_column_aborts_before_writing_anything():
    api = FakeApi(["Name", "Plataform", "Link", "Contact", "Contact Type", "Status"])
    with pytest.raises(HeaderMismatch):
        TargetSheet(api, "Target List", MAPPING).append([qualified()])
    assert api.appended == []


def test_a_missing_column_aborts_before_writing_anything():
    api = FakeApi(["Name", "Platform", "Link"])
    with pytest.raises(HeaderMismatch):
        TargetSheet(api, "Target List", MAPPING).append([qualified()])
    assert api.appended == []


def test_extra_columns_are_tolerated():
    api = FakeApi(HEADERS + ["Notes", "Owner"])
    TargetSheet(api, "Target List", MAPPING).append([qualified()])
    assert len(api.appended[0]) == len(HEADERS) + 2


def test_reordered_columns_follow_the_header_not_the_mapping():
    api = FakeApi(["Platform", "Name", "Link", "Contact", "Contact Type", "Status"])
    TargetSheet(api, "Target List", MAPPING).append([qualified()])
    assert api.appended[0][0] == "podcast"
    assert api.appended[0][1] == "Ada"


def test_a_row_without_a_contact_is_refused():
    bare = Candidate(channel="podcast", person_key="k", display_name="Ada")
    api = FakeApi(HEADERS)
    with pytest.raises(ValueError):
        TargetSheet(api, "Target List", MAPPING).append([bare])
    assert api.appended == []


def test_nothing_is_written_for_an_empty_batch():
    api = FakeApi(HEADERS)
    TargetSheet(api, "Target List", MAPPING).append([])
    assert api.appended == []


def test_the_sheet_client_has_no_update_capability():
    assert not hasattr(TargetSheet, "update")
    assert not hasattr(TargetSheet, "clear")
    assert not hasattr(TargetSheet, "delete")
