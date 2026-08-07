import re
import tomllib
from functools import lru_cache
from urllib.parse import urlparse

from .page import visible_text
from .paths import repo_config_dir

TWO_PART_SUFFIX = {
    "co.uk", "org.uk", "ac.uk", "gov.uk", "co.jp", "co.nz", "co.za", "com.au",
    "com.br", "com.cn", "co.in", "co.kr", "com.mx", "com.tr", "co.il",
}


def host_of(url):
    if not url:
        return None
    host = urlparse(url if "//" in url else f"//{url}").netloc.lower()
    host = host.split("@")[-1].split(":")[0].removeprefix("www.")
    return host or None


def registrable_domain(url):
    host = host_of(url)
    if not host or "." not in host or " " in host:
        return None
    parts = host.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in TWO_PART_SUFFIX:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


AUTHOR_LINK = re.compile(
    r'href=["\'][^"\']*/(?:author|authors|by|contributor|contributors|staff|writers)/'
    r'([A-Za-z0-9._\-]+)',
    re.I,
)
MASTHEAD = re.compile(r"\b(masthead|editorial (staff|team)|our (writers|contributors|newsroom))\b", re.I)


@lru_cache(maxsize=1)
def _config():
    path = repo_config_dir() / "shared_domains.toml"
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _matches(host, names):
    """A shared host is matched by label, never by substring: t.co must not swallow troyhunt.com."""
    return any(host == n or host.endswith(f".{n}") for n in names)


def _is_listed(url, listing):
    host = host_of(url)
    if not host:
        return False
    return _matches(host, listing) or _matches(registrable_domain(url) or "", listing)


def is_platform_host(url):
    return _is_listed(url, _config()["platform_hosts"])


def is_institution(url):
    return _is_listed(url, _config()["institutions"])


def looks_like_a_multi_author_publication(html):
    authors = {a.lower() for a in AUTHOR_LINK.findall(html or "")}
    return len(authors) >= _config()["multi_author_threshold"] or bool(
        MASTHEAD.search(visible_text(html))
    )


def is_a_persons_own_site(url):
    return bool(registrable_domain(url)) and not is_platform_host(url) and not is_institution(url)


def is_a_shared_mailbox(address):
    """An address on a platform's own domain belongs to the platform, not to a person."""
    domain = (address or "").rpartition("@")[2].lower()
    if not domain:
        return False
    return _matches(domain, _config()["platform_hosts"]) or _matches(
        domain, _config()["institutions"]
    )
