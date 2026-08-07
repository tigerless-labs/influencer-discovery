import pytest

from outreach import session as session_module
from outreach.session import NoSession, browser_cookies, rdt_session_ready, x_session_ready


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
