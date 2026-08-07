import subprocess

MISSING_READER = (
    "缺 browser-cookie3,登录态取不到。装:pip install browser-cookie3"
)


class NoSession(Exception):
    pass


def browser_cookies(domain):
    """Reads the登录态 the user already has. Values never leave this process except to that domain."""
    try:
        import browser_cookie3
    except ImportError:
        raise NoSession(MISSING_READER) from None
    try:
        jar = browser_cookie3.chrome(domain_name=domain)
    except Exception as e:
        raise NoSession(f"{domain} 的浏览器 cookie 读不出来:{type(e).__name__}") from None
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
        raise NoSession(f"浏览器里没有 x.com 的 {'、'.join(missing)} —— 先在 Chrome 里登录 x.com")

    added = _twscrape("add_cookie", label, f"auth_token={jar['auth_token']}; ct0={jar['ct0']}")
    if added.returncode != 0:
        raise NoSession("twscrape 收不下这份 cookie")
    return True


def rdt_session_ready():
    try:
        status = subprocess.run(["rdt", "status"], capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        raise NoSession("缺 rdt CLI。装好后跑一次 `rdt login` 让它接管浏览器 cookie") from None
    if "true" not in status.stdout.lower():
        raise NoSession("rdt 未登录 —— 跑一次 `rdt login`,它会自己从浏览器取 cookie")
    return True
