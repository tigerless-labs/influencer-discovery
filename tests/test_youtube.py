from influencer_discovery.channels.youtube import YouTube, subscribers_from


def test_subscriber_suffixes_scale():
    assert subscribers_from("12.3K subscribers") == 12300
    assert subscribers_from("1.2M subscribers") == 1_200_000
    assert subscribers_from("845 subscribers") == 845
    assert subscribers_from("2,500 subscribers") == 2500


def test_a_page_without_a_count_yields_none():
    assert subscribers_from("no numbers here") is None
    assert subscribers_from("") is None


def test_handles_come_out_of_the_search_payload():
    html = '<script>ytInitialData = {"a":[{"canonicalBaseUrl":"/@alice"},{"canonicalBaseUrl":"/@bob"}]};</script>'
    assert YouTube._handles(html) == ["@alice", "@bob"]


def test_a_channel_id_url_is_not_a_handle():
    html = '<script>ytInitialData = {"a":{"canonicalBaseUrl":"/channel/UC123"}};</script>'
    assert YouTube._handles(html) == []


def test_handles_are_deduped():
    html = '"canonicalBaseUrl":"/@alice" "canonicalBaseUrl":"/@alice"'
    assert YouTube._handles(html) == ["@alice"]


def test_unparseable_json_does_not_crash_discovery():
    assert YouTube._handles("<script>ytInitialData = {broken;</script>") == []
    assert YouTube._handles("") == []


def test_the_channel_name_beats_the_tab_labels():
    html = ('<script>ytInitialData={"tabs":[{"title":"Home"},{"title":"Videos"}],'
            '"metadata":{"channelMetadataRenderer":{"title":"Jane Builds AI"}}};</script>')
    assert YouTube._channel_name(html) == "Jane Builds AI"


def test_an_escaped_channel_name_is_decoded():
    html = '"channelMetadataRenderer":{"title":"Ada \\u0026 Co"}'
    assert YouTube._channel_name(html) == "Ada & Co"


def test_og_title_is_the_fallback():
    assert YouTube._channel_name('<meta property="og:title" content="Fallback Chan">') == "Fallback Chan"


def test_no_name_anywhere_yields_none():
    assert YouTube._channel_name("<html></html>") is None
