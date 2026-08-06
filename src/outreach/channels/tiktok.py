import urllib.parse

from ..hop import emails_in
from ..record import Audience, Candidate, Contact
from .base import Channel, register
from .sociavault import OutOfCredits, SociaVault


@register
class TikTok(Channel):
    name = "tiktok"
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
            found = provider.call("tiktok/search/users", query=urllib.parse.quote(term))
            for user in self._users(found):
                handle = user.get("unique_id") or user.get("uniqueId") or user.get("username")
                if user.get("verified"):
                    continue
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

    @staticmethod
    def _users(found):
        if not found:
            return []
        for key in ("users", "user_list", "results"):
            block = found.get(key)
            if isinstance(block, dict):
                block = list(block.values())
            if isinstance(block, list):
                return [b.get("user_info") or b.get("user") or b for b in block]
        return []

    def _profile(self, provider, handle):
        data = provider.call("tiktok/profile", handle=urllib.parse.quote(handle))
        if not data:
            return None
        user = data.get("user") or data.get("userInfo", {}).get("user") or data
        stats = data.get("stats") or data.get("userInfo", {}).get("stats") or data
        bio = user.get("signature") or ""
        candidate = Candidate(
            channel=self.name,
            person_key=handle,
            display_name=user.get("nickname") or handle,
            profile_url=f"https://www.tiktok.com/@{handle}",
            own_site=user.get("bioLink", {}).get("link") if isinstance(user.get("bioLink"), dict) else user.get("bioLink"),
            audience=Audience(
                value=stats.get("followerCount") or stats.get("follower_count") or 0,
                unit=self.audience_unit,
                as_of="2026-08-06",
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
