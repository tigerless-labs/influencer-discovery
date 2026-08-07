import json
import subprocess

from ..hop import emails_in
from ..record import Audience, Candidate, Contact
from ..session import NoSession, x_session_ready
from ..topic import note_hits
from .base import Channel, register

TIMEOUT_SECONDS = 300


@register
class TwitterX(Channel):
    name = "twitter-x"
    form = "search"
    audience_unit = "followers"
    unavailable = None

    def discover(self, limit):
        try:
            x_session_ready(self.config.get("session_label", "browser"))
        except NoSession as e:
            self.unavailable = str(e)
            return []
        found = {}
        for term in self.config.get("terms", []):
            if len(found) >= limit:
                break
            for tweet in self._search(term, self.config.get("per_term", 40)):
                user = tweet.get("user") or {}
                handle = user.get("username")
                if not handle or handle in found or self.already_have(handle):
                    continue
                candidate = self._to_candidate(user, term)
                if note_hits(candidate):
                    found[handle] = candidate
        return list(found.values())[:limit]

    def _search(self, term, per_term):
        """The session is a real person's, so a dead call is skipped rather than retried."""
        query = f"{term} {self.config.get('filters', '')}".strip()
        proc = subprocess.run(
            ["twscrape", "search", query, "--limit", str(per_term)],
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
        )
        rows = []
        for line in proc.stdout.splitlines():
            if not line.startswith("{"):
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows

    def _to_candidate(self, user, term):
        handle = user["username"]
        bio = user.get("rawDescription") or ""
        links = [
            link.get("url")
            for link in user.get("descriptionLinks") or []
            if isinstance(link, dict) and link.get("url")
        ]
        off_platform = [u for u in links if "x.com" not in u and "twitter.com" not in u]
        candidate = Candidate(
            channel=self.name,
            person_key=handle,
            display_name=user.get("displayname") or handle,
            profile_url=f"https://x.com/{handle}",
            own_site=off_platform[0] if off_platform else None,
            audience=Audience(user.get("followersCount") or 0, self.audience_unit, "2026-08-07"),
            bio=bio,
            payload={
                "term": term,
                "statusesCount": user.get("statusesCount"),
                "location": user.get("location"),
                "verified": user.get("verified") or user.get("blue"),
            },
        )
        for address in emails_in(bio):
            candidate.add_contact(Contact(address, "email", "platform_bio"))
            break
        candidate.mark_checked("profile")
        return candidate
