import json
import subprocess

from ..domains import is_a_persons_own_site
from ..hop import registrable_domain
from ..record import Candidate
from .base import Channel, register


@register
class Reddit(Channel):
    name = "reddit"
    form = "search"

    def discover(self, limit):
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
        return list(found.values())[:limit]

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
