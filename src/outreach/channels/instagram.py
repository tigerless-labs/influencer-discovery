import urllib.parse

from ..hop import emails_in
from ..record import Audience, Candidate, Contact
from ..topic import note_hits
from .base import Channel, register
from .scrapecreators import OutOfCredits, ScrapeCreators


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
        for term in self.config.get("terms", []):
            if len(found) >= limit:
                break
            try:
                data = provider.call(
                    "v1/instagram/search/profiles", query=urllib.parse.quote(term)
                )
            except OutOfCredits:
                break
            for profile in (data or {}).get("profiles", []):
                handle = profile.get("username")
                if not handle or handle in found or self.already_have(handle):
                    continue
                candidate = self._from_search(profile, term)
                if note_hits(candidate):
                    found[handle] = candidate

        for candidate in list(found.values()):
            try:
                self._add_followers(provider, candidate)
            except OutOfCredits:
                break
        return list(found.values())[:limit]

    def _from_search(self, profile, term):
        handle = profile["username"]
        bio = profile.get("biography") or ""
        links = [
            link.get("url") if isinstance(link, dict) else link
            for link in profile.get("bio_links") or []
        ]
        links = [l for l in links if isinstance(l, str) and l.startswith("http")]
        candidate = Candidate(
            channel=self.name,
            person_key=handle,
            display_name=profile.get("full_name") or handle,
            profile_url=f"https://instagram.com/{handle}",
            own_site=profile.get("external_url") or (links[0] if links else None),
            bio=bio,
            payload={
                "term": term,
                "category": profile.get("category_name"),
                "is_business_account": profile.get("is_business_account"),
                "is_verified": profile.get("is_verified"),
            },
        )
        for address in emails_in(bio):
            candidate.add_contact(Contact(address, "email", "platform_bio"))
            break
        return candidate

    def _add_followers(self, provider, candidate):
        """The count only orders the results, so it is fetched after the topic gate, not before."""
        data = provider.call("v1/instagram/profile", handle=candidate.person_key)
        candidate.mark_checked("profile")
        user = ((data or {}).get("data") or {}).get("user") or {}
        count = user.get("follower_count") or (user.get("edge_followed_by") or {}).get("count")
        if count:
            candidate.audience = Audience(count, self.audience_unit, "2026-08-07")
        if not candidate.own_site and user.get("external_url"):
            candidate.own_site = user["external_url"]
