import re
from urllib.parse import urlparse

EMAIL = re.compile(r"(?<!@)\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

ROLE_LOCAL = {
    "info", "contact", "support", "help", "admin", "webmaster", "postmaster", "abuse",
    "press", "media", "editor", "editors", "editorial", "news", "newsroom", "tips",
    "sales", "billing", "accounts", "subscriptions", "subscribe", "careers", "jobs",
    "legal", "privacy", "security", "feedback", "team", "office", "enquiries",
    "inquiries", "general", "mail", "service", "customerservice",
}

PLACEHOLDER_LOCAL = {
    "you", "your", "youremail", "your.email", "name", "yourname", "email",
    "someone", "user", "username", "example", "firstname", "lastname",
    "sentry", "noreply", "no-reply", "donotreply", "do-not-reply",
}
PLACEHOLDER_DOMAIN = {
    "example.com", "example.org", "example.net", "domain.com", "yourdomain.com",
    "here.com", "email.com", "sentry.io", "wixpress.com",
}
ASSET_SUFFIX = re.compile(r"@\d+x\.(png|jpe?g|gif|webp|svg)$", re.I)

SPONSOR_PATH = re.compile(
    r"/(sponsor|sponsors|sponsorship|advertise|advertising|advertisers|media-?kit"
    r"|work-?with-?me|partnerships?|collab\w*|brand-?deals?|rate-?card)(/|$|\?)",
    re.I,
)
CONTACTISH = re.compile(r"(contact|about|impressum|hire|colofon|connect)", re.I)

SPONSOR_TEXT = re.compile(
    r"(sponsor(ed|ship|s)? (by|this|inquir|opportunit)|advertise (with|on) (us|this|the)"
    r"|media ?kit|rate ?card|brand (deal|partnership)|work with me|partner with (me|us)"
    r"|book a sponsorship|this (episode|newsletter|issue) is sponsored)",
    re.I,
)


def mentions_sponsorship(text):
    return bool(SPONSOR_TEXT.search(text or ""))

TWO_PART_SUFFIX = {
    "co.uk", "org.uk", "ac.uk", "gov.uk", "co.jp", "co.nz", "co.za", "com.au",
    "com.br", "com.cn", "co.in", "co.kr", "com.mx", "com.tr", "co.il",
}


def registrable_domain(url):
    if not url:
        return None
    host = urlparse(url if "//" in url else f"//{url}").netloc.lower()
    host = host.split("@")[-1].split(":")[0].removeprefix("www.")
    if not host or "." not in host or " " in host:
        return None
    parts = host.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in TWO_PART_SUFFIX:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def emails_in(text):
    found = []
    for raw in EMAIL.findall(text or ""):
        if ASSET_SUFFIX.search(raw):
            continue
        local, _, domain = raw.rpartition("@")
        if local.lower() in PLACEHOLDER_LOCAL or domain.lower() in PLACEHOLDER_DOMAIN:
            continue
        if domain.lower().endswith(".sentry.io") or "ingest.sentry.io" in domain.lower():
            continue
        if local.lower() in ROLE_LOCAL:
            continue
        if raw.lower() not in {e.lower() for e in found}:
            found.append(raw.lower())
    return found


def is_directory_page(addresses, threshold=5):
    domains = {a.rpartition("@")[2] for a in addresses}
    return len(domains) >= threshold


def looks_like_sponsor_page(url):
    return bool(SPONSOR_PATH.search(urlparse(url).path or "/"))


def looks_contactish(url):
    return bool(CONTACTISH.search(urlparse(url).path or "/"))


LINK = re.compile(r'href=["\']([^"\']+)["\']', re.I)


def internal_links(html, base_url):
    base = registrable_domain(base_url)
    out = []
    for href in LINK.findall(html or ""):
        if href.startswith(("mailto:", "javascript:", "#")):
            continue
        url = href if href.startswith("http") else base_url.rstrip("/") + "/" + href.lstrip("/")
        if registrable_domain(url) == base and url not in out:
            out.append(url)
    return out


def mailto_addresses(html):
    return emails_in(" ".join(re.findall(r'href=["\']mailto:([^"\'?]+)', html or "", re.I)))
