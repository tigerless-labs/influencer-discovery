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


REDDIT_DUMP = "\n".join([
    '{"user":"blogger","status":200,"social_links":[{"type":"CUSTOM","url":"https://blogger.dev"}]}',
    '{"user":"linked","status":200,"social_links":[{"type":"CUSTOM","url":"https://www.linkedin.com/in/x"}]}',
    '{"user":"platformed","status":200,"social_links":[{"type":"TWITTER","url":"https://x.com/y"}]}',
    '{"user":"bare","status":200,"social_links":[]}',
    "{ not json",
    "",
])


def dump(tmp_path, text=REDDIT_DUMP):
    path = tmp_path / "profiles.jsonl"
    path.write_text(text, encoding="utf-8")
    return {"profile_dumps": [str(path)]}


def by_key(candidates):
    return {c.person_key: c for c in candidates}


def test_a_declared_own_domain_becomes_the_second_hop_target(tmp_path):
    from outreach.channels.reddit import Reddit

    found = by_key(Reddit(None, dump(tmp_path))._from_dumps(50))
    assert found["blogger"].own_site == "https://blogger.dev"
    assert found["blogger"].profile_url.endswith("/blogger")


def test_a_platform_address_typed_into_the_custom_field_is_not_an_own_site(tmp_path):
    from outreach.channels.reddit import Reddit

    found = by_key(Reddit(None, dump(tmp_path))._from_dumps(50))
    assert found["linked"].own_site is None
    assert found["platformed"].own_site is None


def test_someone_with_no_links_still_enters_the_log(tmp_path):
    """Crawled is crawled: leaving them out means paying for them again next round."""
    from outreach.channels.reddit import Reddit

    assert "bare" in by_key(Reddit(None, dump(tmp_path))._from_dumps(50))


def test_a_malformed_line_is_skipped_not_fatal(tmp_path):
    from outreach.channels.reddit import Reddit

    assert len(Reddit(None, dump(tmp_path))._from_dumps(50)) == 4


def test_people_with_a_site_are_offered_before_people_without(tmp_path):
    from outreach.channels.reddit import Reddit

    sites = [bool(c.own_site) for c in Reddit(None, dump(tmp_path))._from_dumps(50)]
    assert sites == sorted(sites, reverse=True)


def test_the_dump_survives_a_missing_reddit_session(tmp_path, monkeypatch):
    from outreach.channels import reddit as module

    def no_session():
        raise module.NoSession("no cookie")

    monkeypatch.setattr(module, "rdt_session_ready", no_session)
    channel = module.Reddit(None, dump(tmp_path))
    assert len(channel.discover(50)) == 4
    assert channel.unavailable


def test_a_dump_that_is_not_there_is_not_an_error(tmp_path):
    from outreach.channels.reddit import Reddit

    assert Reddit(None, {"profile_dumps": [str(tmp_path / "gone.jsonl")]})._from_dumps(50) == []
