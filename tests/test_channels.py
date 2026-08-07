from outreach.channels.instagram import Instagram
from outreach.channels.threads import Threads
from outreach.channels.tiktok import TikTok

IG_SEARCH_PROFILE = {
    "username": "fixture_person",
    "full_name": "Fixture Person",
    "biography": "AI agents, LLM tooling. reach me at hi@fixtureperson.dev",
    "external_url": "https://fixtureperson.dev",
    "bio_links": [{"url": "https://fixtureperson.dev"}],
    "is_verified": False,
    "category_name": "Blogger",
}

IG_PROFILE = {"data": {"user": {"edge_followed_by": {"count": 42000}}}}

TT_PROFILE = {
    "user": {"uniqueId": "fx", "nickname": "FX", "signature": "ai tools. hi@fx.dev",
             "bioLink": {"link": "https://fx.dev"}, "verified": False},
    "stats": {"followerCount": 53300, "videoCount": 90},
}

TH_PROFILE = {
    "username": "fx", "full_name": "FX", "biography": "prompt engineering. hi@fx.dev",
    "follower_count": 18000, "is_verified": False,
}


class Provider:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def call(self, path, **params):
        self.calls.append(path)
        return self.payload


def test_an_instagram_search_row_carries_bio_site_and_address():
    c = Instagram(None, {})._from_search(IG_SEARCH_PROFILE, "ai")
    assert c.own_site == "https://fixtureperson.dev"
    assert c.email == "hi@fixtureperson.dev"
    assert c.contacts[0].source == "platform_bio"


def test_the_instagram_search_row_has_no_follower_count():
    c = Instagram(None, {})._from_search(IG_SEARCH_PROFILE, "ai")
    assert c.audience is None


def test_the_follower_count_comes_from_the_second_call():
    channel = Instagram(None, {})
    c = channel._from_search(IG_SEARCH_PROFILE, "ai")
    channel._add_followers(Provider(IG_PROFILE), c)
    assert c.audience.value == 42000
    assert c.audience.unit == "followers"
    assert c.was_checked("profile")


def test_a_tiktok_profile_yields_followers_bio_and_link():
    c = TikTok(None, {})._profile(Provider(TT_PROFILE), "fx")
    assert c.audience.value == 53300
    assert c.own_site == "https://fx.dev"
    assert c.email == "hi@fx.dev"


def test_a_threads_profile_yields_followers_and_bio():
    c = Threads(None, {})._profile(Provider(TH_PROFILE), "fx")
    assert c.audience.value == 18000
    assert c.email == "hi@fx.dev"


def test_a_missing_follower_count_does_not_become_a_silent_zero_unit():
    c = TikTok(None, {})._profile(Provider({"user": {"uniqueId": "x"}, "stats": {}}), "x")
    assert c.audience.unit == "followers"
    assert c.audience.value == 0


def test_a_dead_provider_response_yields_no_candidate():
    assert TikTok(None, {})._profile(Provider(None), "x") is None
    assert Threads(None, {})._profile(Provider(None), "x") is None


def test_only_scrapecreators_is_wired_in():
    import outreach.channels as registry

    sources = [
        __import__(f"outreach.channels.{m}", fromlist=["x"]).__file__
        for m in ("instagram", "tiktok", "threads")
    ]
    for path in sources:
        text = open(path).read()
        assert "sociavault" not in text.lower()
        assert "ScrapeCreators" in text
    assert "threads" in registry.known()
