import re
from urllib.parse import urlparse

from .domains import is_a_shared_mailbox, registrable_domain
from .page import visible_text

EMAIL = re.compile(r"(?<!@)\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

ROLE_LOCAL = {
    "info", "contact", "support", "help", "admin", "webmaster", "postmaster", "abuse",
    "press", "media", "editor", "editors", "editorial", "news", "newsroom", "tips",
    "sales", "billing", "accounts", "subscriptions", "subscribe", "careers", "jobs",
    "legal", "privacy", "security", "feedback", "team", "office", "enquiries",
    "inquiries", "general", "mail", "service", "customerservice",
    "partners", "partnerships", "advertise", "advertising", "ads", "sponsor", "sponsors",
    "git", "noreply", "no-reply",
}

IMAGE_TLD = {"png", "jpg", "jpeg", "gif", "webp", "svg", "avif", "ico"}

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


def mentions_sponsorship(html):
    return bool(SPONSOR_TEXT.search(visible_text(html)))

def is_an_inbox(address):
    if not address or ASSET_SUFFIX.search(address):
        return False
    local, _, domain = address.rpartition("@")
    local, domain = local.lower(), domain.lower()
    if not local or "." not in domain:
        return False
    if domain.rpartition(".")[2] in IMAGE_TLD:
        return False
    if local in PLACEHOLDER_LOCAL or domain in PLACEHOLDER_DOMAIN:
        return False
    if domain.endswith(".sentry.io") or "ingest.sentry.io" in domain:
        return False
    if local in ROLE_LOCAL:
        return False
    return not is_a_shared_mailbox(address)


def emails_in(text):
    found = []
    for raw in EMAIL.findall(text or ""):
        if not is_an_inbox(raw):
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
