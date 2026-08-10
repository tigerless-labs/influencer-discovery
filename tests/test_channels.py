from influencer_discovery.channels.instagram import Instagram
from influencer_discovery.channels.threads import Threads
from influencer_discovery.channels.tiktok import TikTok

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
    import influencer_discovery.channels as registry

    sources = [
        __import__(f"influencer_discovery.channels.{m}", fromlist=["x"]).__file__
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
    from influencer_discovery.channels.reddit import Reddit

    found = by_key(Reddit(None, dump(tmp_path))._from_dumps(50))
    assert found["blogger"].own_site == "https://blogger.dev"
    assert found["blogger"].profile_url.endswith("/blogger")


def test_a_platform_address_typed_into_the_custom_field_is_not_an_own_site(tmp_path):
    from influencer_discovery.channels.reddit import Reddit

    found = by_key(Reddit(None, dump(tmp_path))._from_dumps(50))
    assert found["linked"].own_site is None
    assert found["platformed"].own_site is None


def test_someone_with_no_links_still_enters_the_log(tmp_path):
    """Crawled is crawled: leaving them out means paying for them again next round."""
    from influencer_discovery.channels.reddit import Reddit

    assert "bare" in by_key(Reddit(None, dump(tmp_path))._from_dumps(50))


def test_a_malformed_line_is_skipped_not_fatal(tmp_path):
    from influencer_discovery.channels.reddit import Reddit

    assert len(Reddit(None, dump(tmp_path))._from_dumps(50)) == 4


def test_people_with_a_site_are_offered_before_people_without(tmp_path):
    from influencer_discovery.channels.reddit import Reddit

    sites = [bool(c.own_site) for c in Reddit(None, dump(tmp_path))._from_dumps(50)]
    assert sites == sorted(sites, reverse=True)


def test_the_dump_survives_a_missing_reddit_session(tmp_path, monkeypatch):
    from influencer_discovery.channels import reddit as module

    def no_session():
        raise module.NoSession("no cookie")

    monkeypatch.setattr(module, "rdt_session_ready", no_session)
    channel = module.Reddit(None, dump(tmp_path))
    assert len(channel.discover(50)) == 4
    assert channel.unavailable


def test_a_dump_that_is_not_there_is_not_an_error(tmp_path):
    from influencer_discovery.channels.reddit import Reddit

    assert Reddit(None, {"profile_dumps": [str(tmp_path / "gone.jsonl")]})._from_dumps(50) == []


def tracker(kind, url):
    """Reddit ships this attribute HTML-escaped; a fixture with raw quotes would test a page that does not exist."""
    blob = (f'{{&quot;social_link&quot;:{{&quot;type&quot;:&quot;{kind}&quot;,'
            f'&quot;url&quot;:&quot;{url}&quot;}}}}')
    return f'<faceplate-tracker noun="social_link" data-faceplate-tracking-context="{blob}"></faceplate-tracker>'


PROFILE_HTML = (
    "<html><body>"
    + tracker("CUSTOM", "https://blogger.dev")
    + tracker("TWITTER", "https://x.com/blogger")
    + "<span>33882 followers</span></body></html>"
)


def test_a_profile_page_gives_both_the_domain_and_the_size():
    from influencer_discovery.channels.reddit import Reddit

    channel = Reddit(None, {})
    assert channel._own_domain(channel._social_links(PROFILE_HTML)) == "https://blogger.dev"
    assert channel._followers(PROFILE_HTML) == 33882


def test_a_shortened_follower_count_is_read_at_its_real_scale():
    from influencer_discovery.channels.reddit import Reddit

    channel = Reddit(None, {})
    assert channel._followers("<span>12.4k followers</span>") == 12400
    assert channel._followers("<span>1,204 followers</span>") == 1204
    assert channel._followers("<span>2m followers</span>") == 2_000_000


def test_the_same_figure_repeated_is_still_a_size():
    from influencer_discovery.channels.reddit import Reddit

    assert Reddit(None, {})._followers("<b>4210 followers</b><i>4,210 followers</i>") == 4210


def test_a_tracking_blob_that_is_not_json_does_not_kill_the_page():
    from influencer_discovery.channels.reddit import Reddit

    html = '<faceplate-tracker data-faceplate-tracking-context="{oops social_link"></faceplate-tracker>' + PROFILE_HTML
    assert Reddit(None, {})._social_links(html)


def test_a_dump_does_not_re_offer_people_the_log_already_holds(tmp_path):
    """Otherwise the already-imported crowd eats the whole budget and the live path never runs."""
    from influencer_discovery.channels.reddit import Reddit

    channel = Reddit(None, dump(tmp_path))
    channel.already_have = lambda key: key == "blogger"
    assert "blogger" not in by_key(channel._from_dumps(50))


def test_a_page_with_no_follower_widget_means_zero_not_unknown():
    """Reddit only renders the count above zero, so absence is the number, not a gap."""
    from influencer_discovery.channels.reddit import Reddit

    assert Reddit(None, {})._followers("<html><body>a profile with no widget</body></html>") == 0
    assert Reddit(None, {})._followers(PROFILE_HTML) == 33882


def test_two_different_figures_still_leave_it_unknown():
    from influencer_discovery.channels.reddit import Reddit

    html = "<p>my friend has 900000 followers</p><span>4210 followers</span>"
    assert Reddit(None, {})._followers(html) is None


def test_karma_is_read_from_the_user_record():
    from influencer_discovery.channels.reddit import Reddit

    payload = {"data": {"total_karma": 4321, "link_karma": 1, "comment_karma": 2}}
    assert Reddit(None, {})._karma(payload) == 4321
    assert Reddit(None, {})._karma({"data": {}}) is None
    assert Reddit(None, {})._karma(None) is None


def test_karma_stands_in_only_when_nobody_follows_him():
    """A real follower count is the audience; karma is only a proxy for platforms without one."""
    from influencer_discovery.channels.reddit import Reddit
    from influencer_discovery.record import Audience

    channel = Reddit(None, {})
    assert channel._audience(followers=5400, karma=90).unit == "followers"
    assert channel._audience(followers=0, karma=9000) == Audience(9000, "karma", channel._today)
    assert channel._audience(followers=0, karma=None) == Audience(0, "followers", channel._today)
    assert channel._audience(followers=None, karma=None) is None
