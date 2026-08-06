import re
import tomllib
from functools import lru_cache

from .hop import registrable_domain
from .paths import repo_config_dir

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


def _matches(domain, names):
    return any(domain == n or domain.endswith(f".{n}") for n in names)


def is_platform_host(url):
    domain = registrable_domain(url)
    if not domain:
        return False
    host = (url or "").lower()
    return _matches(domain, _config()["platform_hosts"]) or any(
        p in host for p in _config()["platform_hosts"]
    )


def is_institution(url):
    domain = registrable_domain(url)
    return bool(domain) and _matches(domain, _config()["institutions"])


def looks_like_a_multi_author_publication(html):
    authors = {a.lower() for a in AUTHOR_LINK.findall(html or "")}
    return len(authors) >= _config()["multi_author_threshold"] or bool(MASTHEAD.search(html or ""))


def is_a_persons_own_site(url):
    return bool(registrable_domain(url)) and not is_platform_host(url) and not is_institution(url)
