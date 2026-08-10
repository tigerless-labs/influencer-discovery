import pytest

from influencer_discovery import session as session_module
from influencer_discovery.session import NoSession, browser_cookies, rdt_session_ready, x_session_ready


class Ran:
    def __init__(self, code=0, out=""):
        self.returncode = code
        self.stdout = out
        self.stderr = ""


def test_a_missing_cookie_reader_names_its_install_command(monkeypatch):
    monkeypatch.setattr(session_module, "browser_cookies", browser_cookies)
    import builtins

    real = builtins.__import__

    def blocked(name, *a, **k):
        if name == "browser_cookie3":
            raise ImportError(name)
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", blocked)
    with pytest.raises(NoSession) as e:
        browser_cookies("x.com")
    assert "pip install browser-cookie3" in str(e.value)


def test_an_existing_account_is_not_re_added(monkeypatch):
    calls = []
    monkeypatch.setattr(session_module, "_twscrape",
                        lambda *a, **k: calls.append(a) or Ran(0, "username  browser  1"))
    assert x_session_ready("browser") is True
    assert calls == [("accounts",)]


def test_an_empty_pool_is_topped_up_from_the_browser(monkeypatch):
    calls = []

    def fake(*a, **k):
        calls.append(a[0])
        return Ran(0, "" if a[0] == "accounts" else "added")

    monkeypatch.setattr(session_module, "_twscrape", fake)
    monkeypatch.setattr(session_module, "browser_cookies",
                        lambda d: {"auth_token": "a", "ct0": "c"})
    assert x_session_ready("browser") is True
    assert calls == ["accounts", "add_cookie"]


def test_a_browser_without_the_login_says_so(monkeypatch):
    monkeypatch.setattr(session_module, "_twscrape", lambda *a, **k: Ran(0, ""))
    monkeypatch.setattr(session_module, "browser_cookies", lambda d: {"ct0": "c"})
    with pytest.raises(NoSession) as e:
        x_session_ready()
    assert "auth_token" in str(e.value)


def test_a_logged_out_rdt_says_what_to_run(monkeypatch):
    monkeypatch.setattr(session_module.subprocess, "run",
                        lambda *a, **k: Ran(0, '"authenticated": false'))
    with pytest.raises(NoSession) as e:
        rdt_session_ready()
    assert "rdt login" in str(e.value)


def test_a_logged_in_rdt_passes(monkeypatch):
    monkeypatch.setattr(session_module.subprocess, "run",
                        lambda *a, **k: Ran(0, '"authenticated": !!bool "true"'))
    assert rdt_session_ready() is True


def test_a_missing_rdt_names_the_fix(monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError

    monkeypatch.setattr(session_module.subprocess, "run", boom)
    with pytest.raises(NoSession) as e:
        rdt_session_ready()
    assert "rdt login" in str(e.value)


def test_the_rdt_cookie_is_read_from_where_rdt_keeps_it(tmp_path, monkeypatch):
    import json as _json

    from influencer_discovery import session as module

    store = tmp_path / "credential.json"
    store.write_text(_json.dumps({"cookies": {"reddit_session": "abc", "token_v2": "def"}}))
    monkeypatch.setattr(module, "rdt_credential_file", lambda: store)
    header = module.rdt_cookie_header()
    assert "reddit_session=abc" in header and "token_v2=def" in header


def test_a_cookie_list_is_read_the_same_as_a_cookie_map(tmp_path, monkeypatch):
    import json as _json

    from influencer_discovery import session as module

    store = tmp_path / "credential.json"
    store.write_text(_json.dumps({"cookies": [{"name": "reddit_session", "value": "abc"}]}))
    monkeypatch.setattr(module, "rdt_credential_file", lambda: store)
    assert module.rdt_cookie_header() == "reddit_session=abc"


def test_no_stored_cookie_is_a_missing_session_not_an_empty_header(tmp_path, monkeypatch):
    """An empty Cookie header would silently fetch the anonymous page and look like real data."""
    from influencer_discovery import session as module

    monkeypatch.setattr(module, "rdt_credential_file", lambda: tmp_path / "gone.json")
    with pytest.raises(module.NoSession):
        module.rdt_cookie_header()


def test_a_credential_file_without_cookies_is_also_a_missing_session(tmp_path, monkeypatch):
    import json as _json

    from influencer_discovery import session as module

    store = tmp_path / "credential.json"
    store.write_text(_json.dumps({"cookies": {}}))
    monkeypatch.setattr(module, "rdt_credential_file", lambda: store)
    with pytest.raises(module.NoSession):
        module.rdt_cookie_header()
