import urllib.parse

from ..hop import emails_in
from ..record import Audience, Candidate, Contact
from .base import Channel, register
from .sociavault import OutOfCredits, SociaVault


@register
class Instagram(Channel):
    name = "instagram"
    form = "search"
    audience_unit = "followers"

    def discover(self, limit):
        provider = SociaVault(self.fetcher, self.config.get("credit_budget", 0))
        if not provider.available:
            return []
        handles = []
        for term in self.config.get("terms", []):
            if len(handles) >= limit * 2:
                break
            found = provider.call("instagram/search", query=urllib.parse.quote(term))
            for user in (found or {}).get("users", {}).values():
                if user.get("is_verified"):
                    continue
                handle = user.get("username")
                if handle and handle not in handles:
                    handles.append(handle)

        candidates = []
        for handle in handles:
            if len(candidates) >= limit:
                break
            try:
                candidate = self._profile(provider, handle)
            except OutOfCredits:
                break
            if candidate:
                candidates.append(candidate)
        return candidates

    def _profile(self, provider, handle):
        data = provider.call("instagram/profile", handle=handle, trim="true")
        if not data:
            return None
        user = data.get("user") or data.get("profile") or data
        followers = user.get("follower_count") or (user.get("edge_followed_by") or {}).get("count")
        bio = user.get("biography") or ""
        links = [link.get("url") for link in user.get("bio_links") or [] if link.get("url")]
        candidate = Candidate(
            channel=self.name,
            person_key=handle,
            display_name=user.get("full_name") or handle,
            profile_url=f"https://instagram.com/{handle}",
            own_site=user.get("external_url") or (links[0] if links else None),
            audience=Audience(value=followers or 0, unit=self.audience_unit, as_of="2026-08-06"),
            bio=bio,
            payload={
                "is_business": user.get("is_business_account"),
                "category": user.get("category_name") or user.get("category"),
                "media_count": user.get("media_count"),
            },
        )
        for address in emails_in(bio):
            candidate.add_contact(Contact(address, "email", "platform_bio"))
            break
        if user.get("public_email"):
            candidate.add_contact(Contact(user["public_email"], "email", "platform_field"))
        candidate.mark_checked("profile")
        return candidate
