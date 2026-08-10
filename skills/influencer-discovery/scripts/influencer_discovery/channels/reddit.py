import json
import re
import subprocess
from datetime import date
from html import unescape

from ..domains import is_a_persons_own_site
from ..domains import registrable_domain
from ..paths import skill_dir
from ..record import Audience, Candidate
from ..session import NoSession, rdt_cookie_header, rdt_session_ready
from .base import Channel, register

OWN_DOMAIN_LINK = "CUSTOM"
SOCIAL_LINK_BLOB = re.compile(r'data-faceplate-tracking-context="([^"]*social_link[^"]*)"', re.I)
FOLLOWER_LINE = re.compile(r"([\d][\d,\.]*)\s*([km])?\s*followers", re.I)
SCALE = {"k": 1_000, "m": 1_000_000}


@register
class Reddit(Channel):
    name = "reddit"
    form = "search"
    unavailable = None

    def discover(self, limit):
        found = {c.person_key: c for c in self._from_dumps(limit)}
        for candidate in self._from_profiles(limit - len(found)):
            found.setdefault(candidate.person_key, candidate)
        for candidate in self._from_subreddits(limit - len(found)):
            found.setdefault(candidate.person_key, candidate)
        return list(found.values())[:limit]

    def _authors(self, limit):
        """Posts are cheap and only name people; the profile page is where the person actually is."""
        names, listings = [], []
        for term in self.config.get("terms", []):
            listings.append(["search", term, "--limit", "100"])
        for subreddit in self.config.get("subreddits", []):
            listings.append(["sub", subreddit, "--sort", "top", "--time", "year", "--limit", "100"])
            listings.append(["sub", subreddit, "--sort", "hot", "--limit", "100"])
        seen = set()
        for argv in listings:
            if len(names) >= limit:
                break
            for post in self._listing(argv):
                author = post.get("author")
                if not author or author == "[deleted]" or author in seen:
                    continue
                seen.add(author)
                if self.already_have(author):
                    continue
                names.append(author)
                if len(names) >= limit:
                    break
        return names

    def _from_profiles(self, limit):
        """The declared domain and the follower count live on the same page, behind the same login."""
        if limit <= 0 or not self.fetcher:
            return []
        try:
            cookie = rdt_cookie_header()
        except NoSession as e:
            self.unavailable = str(e)
            return []
        people = []
        for author in self._authors(limit):
            page = self.fetcher.try_get(
                f"https://www.reddit.com/user/{author}/",
                headers={"Cookie": cookie},
                persist=False,
            )
            if page is None:
                continue
            links = self._social_links(page)
            candidate = self._person(author, self._own_domain(links), {"social_links": links})
            followers = self._followers(page)
            candidate.audience = self._audience(followers, self._user_karma(author) if followers == 0 else None)
            candidate.mark_checked("profile")
            people.append(candidate)
        return people

    def _from_dumps(self, limit):
        """Profile pages already harvested elsewhere. No session, no request, no second charge."""
        with_site, without = [], []
        for path in self.config.get("profile_dumps", []):
            for row in self._rows(skill_dir() / path):
                user = row.get("user")
                if not user or str(row.get("status")) != "200" or self.already_have(user):
                    continue
                links = row.get("social_links") or []
                site = self._own_domain(links)
                (with_site if site else without).append(
                    self._person(user, site, {"social_links": links})
                )
        return (with_site + without)[:limit]

    @staticmethod
    def _rows(path):
        if not path.exists():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                yield row

    @staticmethod
    def _social_links(html):
        """Reddit carries these as its own tracking JSON, so they are read, never scraped off the text."""
        links, seen = [], set()
        for blob in SOCIAL_LINK_BLOB.findall(html or ""):
            try:
                context = json.loads(unescape(blob))
            except json.JSONDecodeError:
                continue
            link = (context or {}).get("social_link") or {}
            url = link.get("url")
            if url and url not in seen:
                seen.add(url)
                links.append({"type": link.get("type"), "url": url})
        return links

    _today = date.today().isoformat()

    @staticmethod
    def _followers(html):
        """The count is only rendered above zero, so a page without it states a zero.
        Two different figures mean we cannot tell which is his, and then neither is."""
        if html is None:
            return None
        found = set()
        for number, suffix in FOLLOWER_LINE.findall(html):
            try:
                value = float(number.replace(",", ""))
            except ValueError:
                continue
            found.add(int(value * SCALE.get((suffix or "").lower(), 1)))
        if not found:
            return 0
        return found.pop() if len(found) == 1 else None

    @staticmethod
    def _karma(record):
        value = ((record or {}).get("data") or {}).get("total_karma")
        return value if isinstance(value, int) else None

    def _audience(self, followers, karma):
        """Karma is not an audience; it stands in only where nobody can follow him at all."""
        if followers:
            return Audience(followers, "followers", self._today)
        if followers == 0 and karma:
            return Audience(karma, "karma", self._today)
        if followers == 0:
            return Audience(0, "followers", self._today)
        return None

    @staticmethod
    def _own_domain(links):
        """Only what the person declared as their own, and only when it is not a platform."""
        for link in links or []:
            if not isinstance(link, dict) or link.get("type") != OWN_DOMAIN_LINK:
                continue
            url = link.get("url") or ""
            if is_a_persons_own_site(url):
                return url
        return None

    def _person(self, user, site, row):
        return Candidate(
            channel=self.name,
            person_key=user,
            display_name=user,
            profile_url=f"https://reddit.com/user/{user}",
            own_site=site,
            payload={
                "source": "profile_social_links",
                "declared_links": [
                    link.get("url")
                    for link in row.get("social_links") or []
                    if isinstance(link, dict)
                ],
            },
        )

    def _user_karma(self, author):
        """Cheap next to the profile page, and only asked for when nobody follows him."""
        record = self._json(["user", author])
        return self._karma(record)

    def _from_subreddits(self, limit):
        if limit <= 0:
            return []
        try:
            rdt_session_ready()
        except NoSession as e:
            self.unavailable = str(e)
            return []
        found = {}
        for subreddit in self.config.get("subreddits", []):
            if len(found) >= limit:
                break
            for post in self._listing(["sub", subreddit, "--sort", "top", "--time", "year", "--limit", "60"]):
                if len(found) >= limit:
                    break
                author = post.get("author")
                url = post.get("url") or ""
                domain = registrable_domain(url)
                if not author or author in found or author == "[deleted]":
                    continue
                if not domain or not is_a_persons_own_site(url):
                    continue
                found[author] = Candidate(
                    channel=self.name,
                    person_key=author,
                    display_name=author,
                    profile_url=f"https://reddit.com/user/{author}",
                    own_site=f"https://{domain}",
                    payload={
                        "subreddit": subreddit,
                        "score": post.get("score"),
                        "title": post.get("title"),
                        "linked": url,
                    },
                )
        return list(found.values())

    @staticmethod
    def _json(argv):
        try:
            proc = subprocess.run(
                ["rdt", *argv, "--json"], capture_output=True, text=True, timeout=120,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if proc.returncode != 0:
            return None
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            return None

    def _listing(self, argv):
        data = self._json(argv)
        listing = ((data or {}).get("data") or {}).get("data") or {}
        return [child.get("data") or {} for child in listing.get("children") or []]
