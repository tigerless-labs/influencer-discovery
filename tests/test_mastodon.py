import json

from outreach.channels.mastodon import Mastodon


class FakeFetcher:
    """Answers from a canned map. Anything unmapped is a dead address, like the real web."""

    def __init__(self, pages=None):
        self.pages = pages or {}
        self.asked = []

    def try_json(self, url, headers=None):
        self.asked.append(url)
        body = self.pages.get(url)
        if body is None:
            return None
        return json.loads(json.dumps(body))


def account(acct, **over):
    base = {
        "acct": acct,
        "display_name": acct,
        "url": f"https://mastodon.social/@{acct}",
        "followers_count": 5000,
        "statuses_count": 100,
        "note": "<p>writes about llm agents</p>",
        "fields": [],
        "bot": False,
        "last_status_at": "2026-08-01",
        "created_at": "2020-01-01T00:00:00.000Z",
    }
    base.update(over)
    return base


def field(name, url, verified=False):
    return {
        "name": name,
        "value": f'<a href="{url}" rel="me nofollow"><span>{url}</span></a>',
        "verified_at": "2026-01-01T00:00:00.000Z" if verified else None,
    }


def adapter(pages=None, **config):
    config.setdefault("hosts", [])
    config.setdefault("tags", [])
    return Mastodon(FakeFetcher(pages), config)


def one(account_row, host="mastodon.social", **config):
    return adapter(**config)._to_candidate(account_row, host, "directory")


# --- what counts as the person's own site -------------------------------------------------

def test_a_verified_field_link_is_the_persons_own_site():
    candidate = one(account("ada", fields=[field("Blog", "https://ada.example", verified=True)]))
    assert candidate.own_site == "https://ada.example"
    assert candidate.payload["own_site_verified"] is True


def test_an_unverified_field_link_still_counts_once_it_clears_the_shared_domain_list():
    candidate = one(account("ada", fields=[field("Blog", "https://ada.example")]))
    assert candidate.own_site == "https://ada.example"
    assert candidate.payload["own_site_verified"] is False


def test_a_verified_link_wins_over_an_unverified_one_whatever_the_order():
    fields = [field("Home", "https://first.example"), field("Blog", "https://second.example", verified=True)]
    assert one(account("ada", fields=fields)).own_site == "https://second.example"


def test_a_shared_platform_link_is_never_an_own_site():
    fields = [field("Code", "https://github.com/ada"), field("Chat", "https://twitter.com/ada")]
    assert one(account("ada", fields=fields)) is None


def test_a_verified_platform_link_is_still_not_an_own_site():
    fields = [field("Code", "https://github.com/ada", verified=True)]
    assert one(account("ada", fields=fields)) is None


def test_a_non_http_field_value_is_refused():
    hostile = {
        "name": "Site",
        "value": '<a href="javascript:fetch(\'/drop\')">click</a>',
        "verified_at": "2026-01-01T00:00:00.000Z",
    }
    assert one(account("ada", fields=[hostile])) is None


def test_a_bare_url_in_a_field_is_read_when_there_is_no_anchor():
    plain = {"name": "Site", "value": "https://ada.example/blog", "verified_at": None}
    assert one(account("ada", fields=[plain])).own_site == "https://ada.example/blog"


# --- reachability found on the profile itself ---------------------------------------------

def test_an_email_in_the_bio_reaches_someone_with_no_site_to_walk():
    candidate = one(account("ada", note="<p>llm work, reach me at ada@ada.example</p>"))
    assert candidate.own_site is None
    assert candidate.email == "ada@ada.example"


def test_a_mailto_link_in_a_field_counts_as_reachable():
    mail = {"name": "Mail", "value": '<a href="mailto:ada@ada.example">mail</a>', "verified_at": None}
    assert one(account("ada", fields=[mail])).email == "ada@ada.example"


def test_a_profile_email_never_replaces_the_site_walk():
    """The walk is also where topic evidence comes from, so a site is worth more than a free address."""
    candidate = one(account(
        "ada",
        note="<p>mail ada@ada.example</p>",
        fields=[field("Blog", "https://ada.example")],
    ))
    assert candidate.own_site == "https://ada.example"
    assert candidate.contacts == []


def test_a_fediverse_handle_is_not_an_email_address():
    candidate = one(account("ada", note="<p>alt account @ada@fosstodon.org</p>"))
    assert candidate is None


def test_a_role_address_is_not_a_person():
    assert one(account("ada", note="<p>info@ada.example</p>")) is None


# --- who is dropped ------------------------------------------------------------------------

def test_a_bot_is_not_a_person():
    fields = [field("Blog", "https://ada.example", verified=True)]
    assert one(account("ada", bot=True, fields=fields)) is None


def test_an_account_with_no_way_in_is_dropped():
    assert one(account("ada", fields=[], note="<p>nothing here</p>")) is None


def test_an_account_below_the_follower_floor_is_dropped_before_it_costs_a_walk():
    fields = [field("Blog", "https://ada.example", verified=True)]
    assert one(account("ada", followers_count=40, fields=fields), min_followers=1000) is None
    assert one(account("ada", followers_count=4000, fields=fields), min_followers=1000) is not None


def test_a_missing_follower_count_is_not_a_pass():
    fields = [field("Blog", "https://ada.example", verified=True)]
    assert one(account("ada", followers_count=None, fields=fields), min_followers=1000) is None


def test_an_account_without_an_acct_is_not_a_record():
    assert one({**account("ada"), "acct": ""}) is None
    assert one({"followers_count": 9000}) is None


# --- identity -------------------------------------------------------------------------------

def test_the_key_carries_the_home_instance():
    fields = [field("Blog", "https://ada.example", verified=True)]
    assert one(account("ada", fields=fields), host="fosstodon.org").person_key == "ada@fosstodon.org"


def test_a_remote_account_keeps_the_instance_it_came_from_not_the_one_that_served_it():
    fields = [field("Blog", "https://ada.example", verified=True)]
    candidate = one(account("ada@hachyderm.io", fields=fields), host="mastodon.social")
    assert candidate.person_key == "ada@hachyderm.io"


def test_the_bio_carries_the_field_text_so_topic_evidence_is_not_thrown_away():
    fields = [field("Newsletter", "https://ada.example")]
    bio = one(account("ada", note="<p>hello</p>", fields=fields)).bio
    assert "Newsletter" in bio and "<" not in bio


def test_audience_is_reported_in_followers():
    fields = [field("Blog", "https://ada.example", verified=True)]
    audience = one(account("ada", followers_count=12345, fields=fields)).audience
    assert audience.value == 12345 and audience.unit == "followers"


# --- the directory sweep ---------------------------------------------------------------------

def directory_url(host, offset):
    return (f"https://{host}/api/v1/directory?order=active&local=false"
            f"&limit=80&offset={offset}")


def people(n, start=0, host="mastodon.social"):
    return [
        account(f"p{i}@{host}", fields=[field("Blog", f"https://p{i}.example", verified=True)])
        for i in range(start, start + n)
    ]


def test_the_directory_is_paged_past_the_first_page():
    host = "mastodon.social"
    pages = {
        directory_url(host, 0): people(80, 0),
        directory_url(host, 80): people(80, 80),
        directory_url(host, 160): people(5, 160),
    }
    found = adapter(pages, hosts=[host], max_offset=800).discover(1000)
    assert len(found) == 165


def test_a_short_page_ends_that_host():
    host = "mastodon.social"
    pages = {directory_url(host, 0): people(10)}
    channel = adapter(pages, hosts=[host], max_offset=800)
    channel.discover(1000)
    assert directory_url(host, 80) not in channel.fetcher.asked


def test_paging_stops_at_the_configured_depth():
    host = "mastodon.social"
    pages = {directory_url(host, off): people(80, off) for off in range(0, 2000, 80)}
    channel = adapter(pages, hosts=[host], max_offset=160)
    channel.discover(10000)
    assert directory_url(host, 240) not in channel.fetcher.asked


def test_one_dead_instance_does_not_stop_the_others():
    pages = {directory_url("b.social", 0): people(5, host="b.social")}
    found = adapter(pages, hosts=["a.social", "b.social"], max_offset=80).discover(1000)
    assert len(found) == 5


def test_a_reply_that_is_not_a_list_is_ignored():
    host = "mastodon.social"
    pages = {directory_url(host, 0): {"error": "go away"}}
    assert adapter(pages, hosts=[host], max_offset=80).discover(1000) == []


def test_the_same_person_seen_on_two_instances_is_one_candidate():
    row = account("ada@hachyderm.io", fields=[field("Blog", "https://ada.example", verified=True)])
    pages = {
        directory_url("a.social", 0): [row],
        directory_url("b.social", 0): [row],
    }
    found = adapter(pages, hosts=["a.social", "b.social"], max_offset=80).discover(1000)
    assert [c.person_key for c in found] == ["ada@hachyderm.io"]


def test_someone_already_in_the_log_is_not_discovered_again():
    host = "mastodon.social"
    pages = {directory_url(host, 0): people(5)}
    channel = adapter(pages, hosts=[host], max_offset=80)
    channel.already_have = lambda key: key == "p2@mastodon.social"
    assert "p2@mastodon.social" not in {c.person_key for c in channel.discover(1000)}


# --- the tag timeline -------------------------------------------------------------------------

def tag_url(host, tag, max_id=None):
    url = f"https://{host}/api/v1/timelines/tag/{tag}?limit=40"
    return url + (f"&max_id={max_id}" if max_id else "")


def status(status_id, acct, **over):
    return {"id": status_id, "account": account(acct, **over)}


def test_the_tag_timeline_pages_backwards_by_max_id():
    host = "mastodon.social"
    first = [status(f"10{i}", f"a{i}", fields=[field("B", f"https://a{i}.example")]) for i in range(5)]
    second = [status(f"20{i}", f"b{i}", fields=[field("B", f"https://b{i}.example")]) for i in range(5)]
    pages = {
        tag_url(host, "ai"): first,
        tag_url(host, "ai", "104"): second,
    }
    found = adapter(pages, hosts=[host], tags=["ai"], max_offset=0, tag_hosts=1).discover(1000)
    assert len(found) == 10


def test_a_max_id_that_is_not_an_id_stops_the_tag_walk():
    """The cursor comes back from an untrusted server, so it is never pasted into a url unchecked."""
    host = "mastodon.social"
    pages = {tag_url(host, "ai"): [status("1 OR DROP", "a0", fields=[field("B", "https://a0.example")])]}
    channel = adapter(pages, hosts=[host], tags=["ai"], max_offset=0, tag_hosts=1)
    found = channel.discover(1000)
    assert len(found) == 1
    assert all("DROP" not in url for url in channel.fetcher.asked)


def test_a_tag_name_that_is_not_a_word_is_never_requested():
    host = "mastodon.social"
    channel = adapter({}, hosts=[host], tags=["../../admin", "ai"], max_offset=0, tag_hosts=1)
    channel.discover(1000)
    assert all("admin" not in url for url in channel.fetcher.asked)


def test_a_boost_credits_the_author_not_the_booster():
    host = "mastodon.social"
    boosted = {
        "id": "300",
        "account": account("booster"),
        "reblog": {"id": "299", "account": account(
            "author", fields=[field("B", "https://author.example", verified=True)])},
    }
    pages = {tag_url(host, "ai"): [boosted]}
    found = adapter(pages, hosts=[host], tags=["ai"], max_offset=0, tag_hosts=1).discover(1000)
    assert [c.person_key for c in found] == ["author@mastodon.social"]


def test_the_tag_source_is_kept_on_the_record():
    host = "mastodon.social"
    pages = {tag_url(host, "llm"): [status("1", "a0", fields=[field("B", "https://a0.example")])]}
    found = adapter(pages, hosts=[host], tags=["llm"], max_offset=0, tag_hosts=1).discover(1000)
    assert found[0].payload["source"] == "tag:llm"


# --- what comes out ------------------------------------------------------------------------------

def test_the_biggest_audiences_come_out_first():
    host = "mastodon.social"
    rows = [
        account("small", followers_count=1200, fields=[field("B", "https://small.example")]),
        account("huge", followers_count=90000, fields=[field("B", "https://huge.example")]),
        account("mid", followers_count=8000, fields=[field("B", "https://mid.example")]),
    ]
    pages = {directory_url(host, 0): rows}
    found = adapter(pages, hosts=[host], max_offset=0).discover(1000)
    assert [c.display_name for c in found] == ["huge", "mid", "small"]


def test_the_walk_budget_caps_how_many_sites_are_handed_on():
    host = "mastodon.social"
    rows = [
        account(f"p{i}", followers_count=1000 + i, fields=[field("B", f"https://p{i}.example")])
        for i in range(20)
    ]
    pages = {directory_url(host, 0): rows}
    found = adapter(pages, hosts=[host], max_offset=0, max_candidates=5).discover(1000)
    assert len(found) == 5


def test_reachable_people_are_not_charged_to_the_walk_budget():
    host = "mastodon.social"
    walkers = [
        account(f"p{i}", followers_count=1000 + i, fields=[field("B", f"https://p{i}.example")])
        for i in range(10)
    ]
    reachable = [
        account(f"m{i}", followers_count=2000, note=f"<p>llm, m{i}@m{i}.example</p>")
        for i in range(4)
    ]
    pages = {directory_url(host, 0): walkers + reachable}
    found = adapter(pages, hosts=[host], max_offset=0, max_candidates=3).discover(1000)
    assert len(found) == 7
    assert sum(1 for c in found if c.own_site) == 3


def test_the_run_limit_still_bounds_the_result():
    host = "mastodon.social"
    pages = {directory_url(host, 0): people(80)}
    assert len(adapter(pages, hosts=[host], max_offset=0).discover(9)) == 9


def test_the_channel_reports_itself_as_a_directory():
    assert Mastodon.form == "directory"
    assert adapter().stop_reason() == "paged to the end"
