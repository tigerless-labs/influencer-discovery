from outreach.channels.twitter_x import TwitterX

USER = {
    "username": "fixture_dev",
    "displayname": "Fixture Dev",
    "rawDescription": "building AI agents. hi@fixturedev.io",
    "descriptionLinks": [
        {"url": "https://x.com/fixture_dev"},
        {"url": "https://fixturedev.io"},
    ],
    "followersCount": 18400,
    "statusesCount": 900,
    "location": "Berlin",
    "verified": False,
}


def test_the_search_row_alone_carries_followers_bio_and_link():
    c = TwitterX(None, {})._to_candidate(USER, "ai agents")
    assert c.audience.value == 18400
    assert c.audience.unit == "followers"
    assert c.bio.startswith("building AI agents")
    assert c.own_site == "https://fixturedev.io"


def test_a_link_back_to_the_platform_is_not_an_own_site():
    only_self = dict(USER, descriptionLinks=[{"url": "https://x.com/fixture_dev"}])
    assert TwitterX(None, {})._to_candidate(only_self, "ai").own_site is None


def test_an_address_in_the_bio_is_credited_to_the_platform():
    c = TwitterX(None, {})._to_candidate(USER, "ai")
    assert c.email == "hi@fixturedev.io"
    assert c.contacts[0].source == "platform_bio"


def test_no_second_call_is_needed():
    c = TwitterX(None, {})._to_candidate(USER, "ai")
    assert c.was_checked("profile")


def test_a_user_without_links_still_becomes_a_candidate():
    bare = dict(USER, descriptionLinks=[])
    assert TwitterX(None, {})._to_candidate(bare, "ai").own_site is None


def test_a_missing_follower_count_keeps_its_unit():
    c = TwitterX(None, {})._to_candidate(dict(USER, followersCount=None), "ai")
    assert c.audience.unit == "followers"
    assert c.audience.value == 0
