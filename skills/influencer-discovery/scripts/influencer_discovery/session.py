import json
import subprocess
from pathlib import Path

MISSING_READER = (
    "browser-cookie3 is missing, so the session cannot be read. Install: pip install browser-cookie3"
)


class NoSession(Exception):
    pass


def browser_cookies(domain):
    """Reads the login session the user already has. Values never leave this process except to that domain."""
    try:
        import browser_cookie3
    except ImportError:
        raise NoSession(MISSING_READER) from None
    try:
        jar = browser_cookie3.chrome(domain_name=domain)
    except Exception as e:
        raise NoSession(f"browser cookies for {domain} could not be read: {type(e).__name__}") from None
    return {c.name: c.value for c in jar}


def _twscrape(*args, timeout=90):
    return subprocess.run(["twscrape", *args], capture_output=True, text=True, timeout=timeout)


def x_session_ready(label="browser"):
    """twscrape holds the session; this only tops it up from the browser when it is empty."""
    listed = _twscrape("accounts")
    if listed.returncode == 0 and label in listed.stdout:
        return True

    jar = browser_cookies("x.com")
    missing = [k for k in ("auth_token", "ct0") if not jar.get(k)]
    if missing:
        raise NoSession(f"browser has no {', '.join(missing)} for x.com — log in to x.com in Chrome first")

    added = _twscrape("add_cookie", label, f"auth_token={jar['auth_token']}; ct0={jar['ct0']}")
    if added.returncode != 0:
        raise NoSession("twscrape refused the cookie")
    return True


def rdt_credential_file():
    return Path.home() / ".config" / "rdt-cli" / "credential.json"


def rdt_cookie_header():
    """Reddit hides a profile behind login; rdt already holds that session, so it is reused, not re-asked."""
    stored = rdt_credential_file()
    if not stored.exists():
        raise NoSession("rdt has no stored cookies — run `rdt login` once (install: pip install rdt-cli)")
    try:
        cookies = json.loads(stored.read_text(encoding="utf-8")).get("cookies")
    except (json.JSONDecodeError, OSError):
        raise NoSession("rdt credential file could not be read — rerun `rdt login`") from None
    if isinstance(cookies, dict):
        pairs = list(cookies.items())
    elif isinstance(cookies, list):
        pairs = [(c.get("name"), c.get("value")) for c in cookies if isinstance(c, dict)]
    else:
        pairs = []
    header = "; ".join(f"{k}={v}" for k, v in pairs if k and v)
    if not header:
        raise NoSession("rdt credential file holds no cookies — rerun `rdt login`")
    return header


def rdt_session_ready():
    try:
        status = subprocess.run(["rdt", "status"], capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        raise NoSession("rdt CLI is missing. Install it, then run `rdt login` once so it takes over the browser cookies") from None
    if "true" not in status.stdout.lower():
        raise NoSession("rdt is not logged in — run `rdt login` once; it pulls cookies from the browser itself")
    return True
