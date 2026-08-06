from outreach.channels.instagram import Instagram
from outreach.channels.sociavault import SociaVault

IG_ENVELOPE = {
    "success": True,
    "data": {
        "success": True,
        "credits_charged": 1,
        "data": {
            "user": {
                "username": "fixture_person",
                "full_name": "Fixture Person",
                "biography": "writer. reach me at hi@fixtureperson.dev",
                "external_url": "https://fixtureperson.dev",
                "edge_followed_by": {"count": 42000},
                "bio_links": [{"url": "https://fixtureperson.dev"}],
                "is_verified": False,
                "category_name": "Blogger",
            }
        },
    },
    "credits_used": 1,
    "endpoint": "instagram/profile",
}


class FakeProvider:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def call(self, path, **params):
        self.calls.append(path)
        return SociaVault.unwrap(self.payload)


def test_the_envelope_is_unwrapped_to_the_user_object():
    assert "user" in SociaVault.unwrap(IG_ENVELOPE)


def test_an_instagram_profile_yields_followers_bio_and_site():
    candidate = Instagram(None, {})._profile(FakeProvider(IG_ENVELOPE), "fixture_person")
    assert candidate.audience.value == 42000
    assert candidate.audience.unit == "followers"
    assert candidate.own_site == "https://fixtureperson.dev"


def test_an_address_in_the_bio_is_taken_from_the_platform_field():
    candidate = Instagram(None, {})._profile(FakeProvider(IG_ENVELOPE), "fixture_person")
    assert candidate.email == "hi@fixtureperson.dev"
    assert candidate.contacts[0].source == "platform_bio"


def test_a_missing_follower_count_does_not_become_a_silent_zero_unit():
    stripped = {"data": {"data": {"user": {"username": "x", "biography": ""}}}}
    candidate = Instagram(None, {})._profile(FakeProvider(stripped), "x")
    assert candidate.audience.unit == "followers"
    assert candidate.audience.value == 0


def test_the_profile_call_is_recorded_as_checked():
    candidate = Instagram(None, {})._profile(FakeProvider(IG_ENVELOPE), "fixture_person")
    assert candidate.was_checked("profile")
