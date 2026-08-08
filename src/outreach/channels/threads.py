import urllib.parse
from dataclasses import dataclass, field
from datetime import date, timedelta

from ..domains import is_a_persons_own_site, is_link_aggregator
from ..hop import emails_in
from ..record import Audience, Candidate, Contact
from ..topic import MAX_EVIDENCE, hits_in, note_hits
from .base import Channel, register
from .scrapecreators import OutOfCredits, ScrapeCreators

WINDOW_DAYS = 7
WINDOW_DEPTH = 78
DISCOVERY_SHARE = 0.25


@dataclass
class Seed:
    """All a search result knows about a person: no follower count, no bio, only where they turned up."""

    handle: str
    display_name: str = ""
    appearances: int = 0
    top_like_count: int = 0
    hits: list = field(default_factory=list)


@register
class Threads(Channel):
    name = "threads"
    form = "search"
    audience_unit = "followers"

    def discover(self, limit):
        provider = self._provider()
        if not provider.available:
            return []
        budget = int(self.config.get("credit_budget", 0) or 0)
        share = float(self.config.get("discovery_share", DISCOVERY_SHARE))
        seeds = self.search(provider, max(1, round(budget * share)))

        found = []
        for seed in self.rank(seeds):
            if len(found) >= limit:
                break
            try:
                candidate = self._profile(provider, seed.handle, seed)
            except OutOfCredits:
                break
            if candidate and note_hits(candidate):
                found.append(candidate)
        return found

    def _provider(self):
        return ScrapeCreators(self.fetcher, self.config.get("credit_budget", 0))

    def windows(self, depth):
        """The endpoint has no cursor, so a date window is the only page there is: one week per page."""
        span = int(self.config.get("window_days", WINDOW_DAYS))
        today = date.today()
        pages = [{}]
        for step in range(max(0, depth - 1)):
            end = today - timedelta(days=step * span)
            pages.append(
                {"start_date": (end - timedelta(days=span)).isoformat(), "end_date": end.isoformat()}
            )
        return pages

    def search(self, provider, credits):
        """Every term is walked one page deep before any term goes deeper, so a short budget still spreads."""
        terms = [t for t in self.config.get("terms", []) if t]
        depth = int(self.config.get("window_depth", WINDOW_DEPTH))
        seeds = {}
        spent = 0
        for window in self.windows(depth):
            for term in terms:
                if spent >= credits:
                    return seeds
                try:
                    data = provider.call(
                        "v1/threads/search", query=urllib.parse.quote(term), **window
                    )
                except OutOfCredits:
                    return seeds
                spent += 1
                self._absorb(seeds, data)
        return seeds

    def _absorb(self, seeds, data):
        """A post is hostile input: only the matched vocabulary is kept, never the text it came from."""
        posts = (data or {}).get("posts")
        for post in posts if isinstance(posts, list) else []:
            if not isinstance(post, dict):
                continue
            user = post.get("user")
            if not isinstance(user, dict):
                continue
            handle = user.get("username")
            if not isinstance(handle, str) or not handle:
                continue
            if user.get("text_post_app_is_private") or self.already_have(handle):
                continue
            name = user.get("full_name")
            seed = seeds.setdefault(
                handle, Seed(handle, name if isinstance(name, str) else handle)
            )
            seed.appearances += 1
            likes = post.get("like_count")
            if isinstance(likes, int) and likes > seed.top_like_count:
                seed.top_like_count = likes
            caption = post.get("caption")
            text = caption.get("text") if isinstance(caption, dict) else None
            for term in hits_in(f"{text or ''}\n{seed.display_name}"):
                if term not in seed.hits:
                    seed.hits.append(term)
            del seed.hits[MAX_EVIDENCE:]

    @staticmethod
    def rank(seeds):
        """Nothing before the profile call measures audience, so spend goes to the loudest evidence first."""
        return sorted(
            seeds.values(),
            key=lambda s: (not s.hits, -s.appearances, -s.top_like_count, s.handle),
        )

    def _profile(self, provider, handle, seed=None):
        """The search never carries a follower count; that is why the profile call cannot be skipped."""
        data = provider.call("v1/threads/profile", handle=urllib.parse.quote(handle))
        if not data or data.get("text_post_app_is_private"):
            return None
        bio = data.get("biography") or ""
        followers = data.get("follower_count")
        name = data.get("full_name") or (seed.display_name if seed else None) or handle
        candidate = Candidate(
            channel=self.name,
            person_key=handle,
            display_name=name,
            profile_url=f"https://www.threads.net/@{handle}",
            own_site=self._own_site(self._links(data)),
            audience=Audience(
                followers if isinstance(followers, int) else 0,
                self.audience_unit,
                date.today().isoformat(),
            ),
            bio=bio,
            payload={
                "is_verified": data.get("is_verified"),
                "profile_tags": self._tags(data),
                "appearances": seed.appearances if seed else 0,
                "top_like_count": seed.top_like_count if seed else 0,
            },
        )
        if seed and seed.hits:
            candidate.signals["topic_hits"] = list(seed.hits)
        for address in emails_in(bio):
            candidate.add_contact(Contact(address, "email", "platform_bio"))
            break
        candidate.mark_checked("profile")
        return candidate

    @staticmethod
    def _links(data):
        """Two providers wrap this container differently; the wrapped redirect is never the address."""
        block = data.get("bio_links")
        if isinstance(block, dict):
            block = list(block.values())
        found = []
        for link in block if isinstance(block, list) else []:
            url = link.get("url") if isinstance(link, dict) else link
            if isinstance(url, str) and url.startswith("http") and url not in found:
                found.append(url)
        external = data.get("external_url")
        if isinstance(external, str) and external.startswith("http") and external not in found:
            found.append(external)
        return found

    @staticmethod
    def _own_site(links):
        """Only one site gets walked, so a personal domain outranks a hub and a platform page is no site."""
        for accept in (is_a_persons_own_site, is_link_aggregator):
            for url in links:
                if accept(url):
                    return url
        return None

    @staticmethod
    def _tags(data):
        block = data.get("profile_tags")
        edges = block.get("edges") if isinstance(block, dict) else None
        tags = []
        for edge in edges if isinstance(edges, list) else []:
            node = edge.get("node") if isinstance(edge, dict) else edge
            if isinstance(node, dict):
                tags += [v for v in node.values() if isinstance(v, str)]
            elif isinstance(node, str):
                tags.append(node)
        return tags[:MAX_EVIDENCE]
