import urllib.parse

from ..domains import registrable_domain
from ..fetch import pmap
from ..hop import emails_in
from ..record import Audience, Candidate, Contact
from ..topic import note_hits
from .base import Channel, register
from .scrapecreators import OutOfCredits, ScrapeCreators

SEARCH = "v1/instagram/search/profiles"
PROFILE = "v1/instagram/profile"
LAST_PAGE = 11
MISSES_ALLOWED = 2
WORKERS = 6
AS_OF = "2026-08-07"


@register
class Instagram(Channel):
    name = "instagram"
    form = "search"
    audience_unit = "followers"

    def discover(self, limit):
        provider = ScrapeCreators(self.fetcher, self.config.get("credit_budget", 0))
        if not provider.available:
            return []

        found = {}
        for batch in self._batches():
            if len(found) >= limit:
                break
            for haul in pmap(
                lambda query: self._walk(provider, query, limit),
                batch,
                workers=self.config.get("workers", WORKERS),
            ):
                for handle, candidate in haul.items():
                    found.setdefault(handle, candidate)
        self._buy_missing_counts(provider, found)
        return list(found.values())[:limit]

    def _batches(self):
        """One search takes twenty seconds, so the queries of a batch run side by side;
        the batches themselves stay ordered, plain terms before any widening."""
        terms = list(self.config.get("terms", []))
        if terms:
            yield terms
        for prefix in self.config.get("contact_prefixes", []):
            yield [f"{prefix} {term}" for term in terms]

    def _walk(self, provider, query, limit):
        """The search wraps a Google index: the cursor is a page number, pages run out
        around ten, and a page of nothing new means the query is spent."""
        found, sighted, misses = {}, set(), 0
        cursor = None
        for _ in range(self.config.get("max_pages", LAST_PAGE)):
            params = {"query": urllib.parse.quote(query)}
            if cursor:
                params["cursor"] = cursor
            try:
                data = provider.call(SEARCH, **params)
            except OutOfCredits:
                break
            if not data:
                misses += 1
                if misses > MISSES_ALLOWED:
                    break
                cursor = str(int(cursor or 1) + 1)
                continue
            misses = 0
            if not self._take(data.get("profiles") or [], query, found, sighted):
                break
            cursor = data.get("cursor")
            if not cursor or len(found) >= limit:
                break
        return found

    def _take(self, profiles, query, found, sighted):
        """Counts everyone the page showed, not everyone it added: a page of people already
        in the log is still a page that moved forward."""
        fresh = 0
        for profile in profiles:
            handle = profile.get("username") if isinstance(profile, dict) else None
            if not isinstance(handle, str) or not handle or handle in sighted:
                continue
            sighted.add(handle)
            fresh += 1
            if handle in found or self.already_have(handle):
                continue
            candidate = self._from_search(profile, query)
            if note_hits(candidate):
                found[handle] = candidate
        return fresh

    def _from_search(self, profile, term):
        handle = profile["username"]
        bio = profile.get("biography") or ""
        candidate = Candidate(
            channel=self.name,
            person_key=handle,
            display_name=profile.get("full_name") or handle,
            profile_url=f"https://instagram.com/{handle}",
            own_site=self._own_site(profile),
            audience=self._audience(profile.get("follower_count")),
            bio=bio,
            payload={
                "term": term,
                "category": profile.get("category_name"),
                "is_business_account": profile.get("is_business_account"),
                "is_verified": profile.get("is_verified"),
            },
        )
        if candidate.audience:
            candidate.mark_checked("profile")
        for address in emails_in(bio):
            candidate.add_contact(Contact(address, "email", "platform_bio"))
            break
        return candidate

    def _audience(self, count):
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            return None
        return Audience(count, self.audience_unit, AS_OF)

    def _own_site(self, profile):
        urls = [profile.get("external_url")]
        for link in profile.get("bio_links") or []:
            urls.append(link.get("url") if isinstance(link, dict) else link)
        for url in urls:
            if not isinstance(url, str) or not url.startswith("http"):
                continue
            if registrable_domain(url) != "instagram.com":
                return url
        return None

    def _buy_missing_counts(self, provider, found):
        for candidate in found.values():
            if candidate.audience is not None:
                continue
            try:
                self._add_followers(provider, candidate)
            except OutOfCredits:
                return

    def _add_followers(self, provider, candidate):
        """The paid profile call buys one thing the search withheld, so only the rows
        the search left unmeasured are worth it."""
        data = provider.call(PROFILE, handle=candidate.person_key)
        candidate.mark_checked("profile")
        user = ((data or {}).get("data") or {}).get("user") or {}
        count = user.get("follower_count") or (user.get("edge_followed_by") or {}).get("count")
        candidate.audience = self._audience(count) or candidate.audience
        if not candidate.own_site and user.get("external_url"):
            candidate.own_site = user["external_url"]
