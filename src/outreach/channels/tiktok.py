import re
import urllib.parse
from datetime import date

from ..domains import registrable_domain
from ..hop import emails_in
from ..record import Audience, Candidate, Contact
from ..topic import MAX_EVIDENCE, hits_in
from .base import Channel, register
from .scrapecreators import OutOfCredits, ScrapeCreators

SORTS = ("relevance", "most-liked")

SITE = re.compile(
    r"(?<![\w@.\-/])(?:https?://)?(?:[a-z0-9][a-z0-9\-]*\.)+[a-z]{2,6}(?:/[^\s,;)\]]*)?",
    re.I,
)
BARE_SITE_TLD = {
    "com", "net", "org", "io", "ai", "co", "dev", "me", "app", "xyz", "site", "blog",
    "link", "bio", "tv", "fm", "cc", "ly", "sh", "so", "gg", "page", "shop", "store",
    "tech", "studio", "design", "art", "news", "media", "club", "space", "life",
    "world", "online", "live", "uk", "de", "fr", "es", "it", "nl", "ca", "au", "in",
    "jp", "kr", "br", "eu", "ee",
}


def site_in(text):
    """A bio is free text, so an address is only taken when it is unmistakably one."""
    for match in SITE.finditer(text or ""):
        found = match.group(0).rstrip(".,;)")
        if found.lower().startswith("http"):
            return found if registrable_domain(found) else None
        host = found.partition("/")[0]
        if "/" not in found and host.rpartition(".")[2].lower() not in BARE_SITE_TLD:
            continue
        if registrable_domain(host):
            return f"https://{found}"
    return None


@register
class TikTok(Channel):
    """Content search says who posts about the subject; the follower count says who to pay for."""

    name = "tiktok"
    form = "search"
    audience_unit = "followers"

    def discover(self, limit):
        provider = ScrapeCreators(self.fetcher, self.config.get("credit_budget", 0))
        if not provider.available:
            return []
        return self.collect(provider, limit)

    def collect(self, provider, limit):
        found = []
        for author in self._spending_order(self._pool(provider)):
            if len(found) >= limit:
                break
            try:
                candidate = self._profile(provider, author["handle"])
            except OutOfCredits:
                break
            if candidate is None:
                continue
            self._carry(candidate, author)
            found.append(candidate)
        return found

    def _pool(self, provider):
        pool = {}
        for term in self.config.get("terms", []):
            for sort_by in SORTS:
                try:
                    self._crawl(provider, term, sort_by, pool)
                except OutOfCredits:
                    return pool
        return pool

    def _crawl(self, provider, term, sort_by, pool):
        """A page that brings nobody new is the end of the term, whatever has_more claims."""
        cursor = 0
        while True:
            data = provider.call(
                "v1/tiktok/search/keyword",
                query=urllib.parse.quote(term),
                sort_by=sort_by,
                cursor=cursor,
            )
            if not data:
                return
            added = sum(
                self._remember(pool, author, caption, plays, term)
                for author, caption, plays in self._videos(data)
            )
            ahead = data.get("cursor")
            if not data.get("has_more") or not added:
                return
            if not isinstance(ahead, int) or ahead <= cursor:
                return
            cursor = ahead

    @staticmethod
    def _videos(data):
        block = data.get("search_item_list")
        if isinstance(block, dict):
            block = list(block.values())
        for item in block if isinstance(block, list) else []:
            if not isinstance(item, dict):
                continue
            video = item.get("aweme_info") or item
            author = video.get("author") if isinstance(video, dict) else None
            if not isinstance(author, dict):
                continue
            stats = video.get("statistics")
            plays = stats.get("play_count") if isinstance(stats, dict) else 0
            yield author, video.get("desc"), plays if isinstance(plays, int) else 0

    def _remember(self, pool, author, caption, plays, term):
        handle = author.get("unique_id") or author.get("uniqueId")
        if not isinstance(handle, str) or not handle.strip() or self.already_have(handle):
            return 0
        entry = pool.get(handle)
        fresh = entry is None
        if fresh:
            entry = pool[handle] = {
                "handle": handle, "followers": 0, "plays": 0, "videos": 0,
                "terms": [], "hits": [],
            }
        followers = author.get("follower_count")
        if isinstance(followers, int) and followers > entry["followers"]:
            entry["followers"] = followers
        entry["plays"] += plays
        entry["videos"] += 1
        if term not in entry["terms"]:
            entry["terms"].append(term)
        for hit in hits_in(f"{author.get('nickname') or ''} {caption or ''}"):
            if hit not in entry["hits"]:
                entry["hits"].append(hit)
        return 1 if fresh else 0

    @staticmethod
    def _spending_order(pool):
        """Evidence first, then size: the budget runs dry on small unknowns, not on the people we came for."""
        return sorted(
            pool.values(),
            key=lambda a: (0 if a["hits"] else 1, -a["followers"], -a["plays"]),
        )

    @staticmethod
    def _carry(candidate, author):
        """What the search already paid for: the captions are evidence, the term is not."""
        hits = candidate.signals.get("topic_hits") or []
        for hit in author["hits"]:
            if hit not in hits:
                hits.append(hit)
        candidate.signals["topic_hits"] = hits[:MAX_EVIDENCE]
        candidate.payload["found_by"] = {
            "terms": author["terms"],
            "videos": author["videos"],
            "plays": author["plays"],
        }
        if not candidate.audience or not candidate.audience.value:
            candidate.audience = Audience(
                author["followers"], TikTok.audience_unit, date.today().isoformat()
            )

    @staticmethod
    def _bio_link(user):
        link = user.get("bioLink")
        if isinstance(link, dict):
            link = link.get("link")
        return link.strip() if isinstance(link, str) and link.strip() else None

    def _profile(self, provider, handle):
        data = provider.call("v1/tiktok/profile", handle=urllib.parse.quote(handle))
        if not data:
            return None
        user = data.get("user") or {}
        stats = data.get("stats") or {}
        bio = user.get("signature") or ""
        candidate = Candidate(
            channel=self.name,
            person_key=handle,
            display_name=user.get("nickname") or handle,
            profile_url=f"https://www.tiktok.com/@{handle}",
            own_site=self._bio_link(user) or site_in(bio),
            audience=Audience(
                stats.get("followerCount") or 0, self.audience_unit, date.today().isoformat()
            ),
            bio=bio,
            payload={
                "videoCount": stats.get("videoCount"),
                "heartCount": stats.get("heartCount"),
                "verified": user.get("verified"),
            },
        )
        for address in emails_in(bio):
            candidate.add_contact(Contact(address, "email", "platform_bio"))
            break
        candidate.mark_checked("profile")
        return candidate
