import re

from ..domains import is_a_persons_own_site
from ..hop import emails_in
from ..page import visible_text
from ..record import Audience, Candidate, Contact
from .base import Channel, register

DIRECTORY = "https://{host}/api/v1/directory?order=active&local=false&limit={page}&offset={offset}"
TAG_TIMELINE = "https://{host}/api/v1/timelines/tag/{tag}?limit={page}"
DIRECTORY_PAGE = 80
TAG_PAGE = 40

DEFAULT_MAX_OFFSET = 160
DEFAULT_MIN_FOLLOWERS = 1000
DEFAULT_MAX_CANDIDATES = 2500
DEFAULT_TAG_PAGES = 5
DEFAULT_TAG_HOSTS = 2
DEFAULT_TAGS = [
    "ai", "artificialintelligence", "llm", "genai", "generativeai",
    "machinelearning", "deeplearning", "chatgpt", "openai", "claude",
    "promptengineering", "aiagents", "aitools", "nlp", "datascience",
    "opensourceai", "ollama", "huggingface", "aiart", "stablediffusion",
    "mlops", "rag", "aiwriting", "aicoding",
]

HREF = re.compile(r'href="([^"]+)"', re.I)
BARE_URL = re.compile(r"https?://[^\s\"'<>]+", re.I)
STATUS_ID = re.compile(r"[A-Za-z0-9_-]{1,40}\Z")
TAG_NAME = re.compile(r"[A-Za-z0-9_]{1,60}\Z")
HTTP = ("http://", "https://")


def _audience_first(candidate):
    return -(candidate.audience.value if candidate.audience else 0)


@register
class Mastodon(Channel):
    """Two entries, one pool: the account directory for reach, tag timelines for the vertical.

    Paging the directory is free, walking a site is not, so the sweep goes as deep as it is
    told to and the walk budget is then spent on the largest audiences it turned up.
    """

    name = "mastodon"
    form = "directory"
    audience_unit = "followers"

    def discover(self, limit):
        found = {}
        self._sweep_directory(found, limit)
        self._sweep_tags(found, limit)
        budget = self.config.get("max_candidates", DEFAULT_MAX_CANDIDATES)
        walkers = sorted((c for c in found.values() if c.own_site), key=_audience_first)
        reachable = [c for c in found.values() if not c.own_site]
        return sorted(walkers[:budget] + reachable, key=_audience_first)[:limit]

    def _sweep_directory(self, found, limit):
        max_offset = self.config.get("max_offset", DEFAULT_MAX_OFFSET)
        for host in self.config.get("hosts", []):
            offset = 0
            while len(found) < limit and offset <= max_offset:
                page = self.fetcher.try_json(
                    DIRECTORY.format(host=host, page=DIRECTORY_PAGE, offset=offset)
                )
                if not isinstance(page, list) or not page:
                    break
                self._absorb(found, page, host, "directory")
                if len(page) < DIRECTORY_PAGE:
                    break
                offset += DIRECTORY_PAGE

    def _sweep_tags(self, found, limit):
        hosts = self.config.get("hosts", [])[: self.config.get("tag_hosts", DEFAULT_TAG_HOSTS)]
        pages = self.config.get("tag_pages", DEFAULT_TAG_PAGES)
        for host in hosts:
            for tag in self.config.get("tags", DEFAULT_TAGS):
                if not TAG_NAME.match(tag or ""):
                    continue
                url = TAG_TIMELINE.format(host=host, tag=tag, page=TAG_PAGE)
                for _ in range(pages):
                    if len(found) >= limit:
                        return
                    statuses = self.fetcher.try_json(url)
                    if not isinstance(statuses, list) or not statuses:
                        break
                    self._absorb(found, self._authors(statuses), host, f"tag:{tag}")
                    cursor = self._cursor(statuses)
                    if not cursor:
                        break
                    url = TAG_TIMELINE.format(host=host, tag=tag, page=TAG_PAGE) + f"&max_id={cursor}"

    @staticmethod
    def _authors(statuses):
        authors = []
        for status in statuses:
            if not isinstance(status, dict):
                continue
            original = status.get("reblog") if isinstance(status.get("reblog"), dict) else status
            account = original.get("account")
            if isinstance(account, dict):
                authors.append(account)
        return authors

    @staticmethod
    def _cursor(statuses):
        """The cursor is whatever the far end says it is, so it is checked before it is a url."""
        last = statuses[-1] if isinstance(statuses[-1], dict) else {}
        cursor = str(last.get("id") or "")
        return cursor if STATUS_ID.match(cursor) else None

    def _absorb(self, found, accounts, host, source):
        for account in accounts:
            candidate = self._to_candidate(account, host, source)
            if not candidate or candidate.person_key in found:
                continue
            if self.already_have(candidate.person_key):
                continue
            found[candidate.person_key] = candidate

    def _to_candidate(self, account, host, source="directory"):
        if not isinstance(account, dict) or account.get("bot"):
            return None
        acct = (account.get("acct") or "").strip()
        if not acct or " " in acct:
            return None
        followers = account.get("followers_count") or 0
        if followers < self.config.get("min_followers", DEFAULT_MIN_FOLLOWERS):
            return None

        fields = [f for f in account.get("fields") or [] if isinstance(f, dict)]
        own_site, verified = self._own_site(fields)
        bio = self._bio(account, fields)
        contacts = [] if own_site else [
            Contact(address, "email", "mastodon_profile")
            for address in emails_in(bio)[:1]
        ]
        if not own_site and not contacts:
            return None

        return Candidate(
            channel=self.name,
            person_key=acct if "@" in acct else f"{acct}@{host}",
            display_name=account.get("display_name") or acct,
            profile_url=account.get("url"),
            own_site=own_site,
            audience=Audience(
                value=followers,
                unit=self.audience_unit,
                as_of=(account.get("last_status_at") or "")[:10],
            ),
            bio=bio,
            contacts=contacts,
            payload={
                "host": host,
                "source": source,
                "own_site_verified": verified,
                "statuses_count": account.get("statuses_count"),
                "created_at": account.get("created_at"),
            },
        )

    @staticmethod
    def _own_site(fields):
        """A verified field is the platform vouching for the link; the rest fall back to the shared list."""
        for wanted in (True, False):
            for field in fields:
                if bool(field.get("verified_at")) is not wanted:
                    continue
                for url in Mastodon._links(field.get("value")):
                    if is_a_persons_own_site(url):
                        return url, wanted
        return None, None

    @staticmethod
    def _links(value):
        found = []
        for url in HREF.findall(value or "") + BARE_URL.findall(visible_text(value)):
            url = url.strip()
            if url.lower().startswith(HTTP) and url not in found:
                found.append(url)
        return found

    @staticmethod
    def _bio(account, fields):
        parts = [visible_text(account.get("note") or "")]
        for field in fields:
            parts.append(str(field.get("name") or ""))
            parts.append(visible_text(field.get("value") or ""))
            parts.extend(HREF.findall(field.get("value") or ""))
        return re.sub(r"\s+", " ", " ".join(parts)).strip()
