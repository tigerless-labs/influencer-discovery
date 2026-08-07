import urllib.parse

from ..hop import emails_in
from ..record import Audience, Candidate, Contact
from ..topic import note_hits
from .base import Channel, register
from .scrapecreators import OutOfCredits, ScrapeCreators


@register
class Threads(Channel):
    name = "threads"
    form = "search"
    audience_unit = "followers"

    def discover(self, limit):
        provider = ScrapeCreators(self.fetcher, self.config.get("credit_budget", 0))
        if not provider.available:
            return []

        handles = []
        for term in self.config.get("terms", []):
            if len(handles) >= limit * 2:
                break
            try:
                data = provider.call("v1/threads/search/users", query=urllib.parse.quote(term))
            except OutOfCredits:
                break
            for user in (data or {}).get("users", []):
                handle = user.get("username")
                if handle and handle not in handles and not self.already_have(handle):
                    handles.append(handle)

        found = []
        for handle in handles:
            if len(found) >= limit:
                break
            try:
                candidate = self._profile(provider, handle)
            except OutOfCredits:
                break
            if candidate and note_hits(candidate):
                found.append(candidate)
        return found

    def _profile(self, provider, handle):
        """The search never carries a follower count; that is why the profile call cannot be skipped."""
        data = provider.call("v1/threads/profile", handle=urllib.parse.quote(handle))
        if not data:
            return None
        bio = data.get("biography") or ""
        links = [
            link.get("url") if isinstance(link, dict) else link
            for link in data.get("bio_links") or []
        ]
        links = [l for l in links if isinstance(l, str) and l.startswith("http")]
        candidate = Candidate(
            channel=self.name,
            person_key=handle,
            display_name=data.get("full_name") or handle,
            profile_url=f"https://www.threads.net/@{handle}",
            own_site=data.get("external_url") or (links[0] if links else None),
            audience=Audience(data.get("follower_count") or 0, self.audience_unit, "2026-08-07"),
            bio=bio,
            payload={"is_verified": data.get("is_verified")},
        )
        for address in emails_in(bio):
            candidate.add_contact(Contact(address, "email", "platform_bio"))
            break
        candidate.mark_checked("profile")
        return candidate
