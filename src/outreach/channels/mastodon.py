import re

from ..domains import is_a_persons_own_site
from ..record import Audience, Candidate
from .base import Channel, register

DIRECTORY = "https://{host}/api/v1/directory?order=active&local=false&limit=80&offset={offset}"
TAG = re.compile(r"<[^>]+>")


@register
class Mastodon(Channel):
    name = "mastodon"
    form = "directory"
    audience_unit = "followers"

    def discover(self, limit):
        found = []
        for host in self.config.get("hosts", []):
            offset = 0
            while len(found) < limit and offset < self.config.get("max_offset", 160):
                accounts = self.fetcher.try_json(DIRECTORY.format(host=host, offset=offset))
                if not accounts:
                    break
                for account in accounts:
                    if len(found) >= limit:
                        break
                    candidate = self._to_candidate(account, host)
                    if candidate:
                        found.append(candidate)
                offset += 80
        return found

    def _to_candidate(self, account, host):
        acct = account.get("acct")
        if not acct or account.get("bot"):
            return None
        verified = [
            f for f in account.get("fields") or [] if f.get("verified_at") and f.get("value")
        ]
        own_site = None
        for field in verified:
            url = re.search(r'href="([^"]+)"', field["value"])
            if url and is_a_persons_own_site(url.group(1)):
                own_site = url.group(1)
                break
        if not own_site:
            return None
        return Candidate(
            channel=self.name,
            person_key=acct if "@" in acct else f"{acct}@{host}",
            display_name=account.get("display_name") or acct,
            profile_url=account.get("url"),
            own_site=own_site,
            audience=Audience(
                value=account.get("followers_count") or 0,
                unit=self.audience_unit,
                as_of=(account.get("last_status_at") or "")[:10],
            ),
            bio=TAG.sub(" ", account.get("note") or ""),
            payload={
                "host": host,
                "statuses_count": account.get("statuses_count"),
                "verified_fields": len(verified),
                "created_at": account.get("created_at"),
            },
        )
