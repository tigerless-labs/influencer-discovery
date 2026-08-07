import json
import subprocess

from ..domains import is_a_persons_own_site
from ..domains import registrable_domain
from ..paths import repo_dir
from ..record import Candidate
from ..session import NoSession, rdt_session_ready
from .base import Channel, register

OWN_DOMAIN_LINK = "CUSTOM"


@register
class Reddit(Channel):
    name = "reddit"
    form = "search"
    unavailable = None

    def discover(self, limit):
        found = {c.person_key: c for c in self._from_dumps(limit)}
        for candidate in self._from_subreddits(limit - len(found)):
            found.setdefault(candidate.person_key, candidate)
        return list(found.values())[:limit]

    def _from_dumps(self, limit):
        """Profile pages already harvested elsewhere. No session, no request, no second charge."""
        with_site, without = [], []
        for path in self.config.get("profile_dumps", []):
            for row in self._rows(repo_dir() / path):
                user = row.get("user")
                if not user or str(row.get("status")) != "200":
                    continue
                site = self._own_domain(row.get("social_links"))
                (with_site if site else without).append(self._person(user, site, row))
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
            for post in self._top(subreddit):
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

    def _top(self, subreddit):
        proc = subprocess.run(
            ["rdt", "sub", subreddit, "--sort", "top", "--time", "year", "--limit", "60", "--json"],
            capture_output=True, text=True, timeout=90,
        )
        if proc.returncode != 0:
            return []
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return []
        listing = ((data or {}).get("data") or {}).get("data") or {}
        return [child.get("data") or {} for child in listing.get("children") or []]
