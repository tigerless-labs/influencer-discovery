import re
import urllib.parse

from ..hop import emails_in, mentions_sponsorship
from ..record import Candidate, Contact
from .base import Channel, normalise_person, register

SEARCH = "https://itunes.apple.com/search?media=podcast&limit=50&term="
OWNER_EMAIL = re.compile(r"<itunes:email>\s*([^<]+)</itunes:email>", re.I)
OWNER_NAME = re.compile(r"<itunes:name>\s*([^<]+)</itunes:name>", re.I)
MANAGING = re.compile(r"<managingEditor>\s*([^<]+)</managingEditor>", re.I)
LINK = re.compile(r"<link>\s*(https?://[^<\s]+)\s*</link>", re.I)


@register
class Podcast(Channel):
    name = "podcast"
    form = "search"

    def discover(self, limit):
        found = []
        for term in self.config.get("terms", []):
            if len(found) >= limit:
                break
            data = self.fetcher.try_json(SEARCH + urllib.parse.quote(term))
            for row in (data or {}).get("results", []):
                if len(found) >= limit:
                    break
                feed = row.get("feedUrl")
                title = row.get("collectionName") or row.get("trackName")
                if not feed or not title:
                    continue
                candidate = Candidate(
                    channel=self.name,
                    person_key=normalise_person(title),
                    display_name=title,
                    profile_url=row.get("trackViewUrl"),
                    payload={
                        "feedUrl": feed,
                        "artistName": row.get("artistName"),
                        "genres": row.get("genres"),
                        "trackCount": row.get("trackCount"),
                        "releaseDate": row.get("releaseDate"),
                        "term": term,
                    },
                )
                if self._read_feed(candidate, feed):
                    found.append(candidate)
        return found

    def _read_feed(self, candidate, feed_url):
        body = self.fetcher.try_get(feed_url)
        candidate.mark_checked("feed")
        if body is None:
            return False
        head = body[:200000]
        owner = OWNER_EMAIL.search(head) or MANAGING.search(head)
        if owner:
            for address in emails_in(owner.group(1)):
                candidate.add_contact(Contact(address, "email", "feed_owner"))
                break
        name = OWNER_NAME.search(head)
        if name:
            candidate.payload["ownerName"] = name.group(1).strip()
        site = LINK.search(head)
        if site and "apple.com" not in site.group(1):
            candidate.own_site = site.group(1).strip()
        if mentions_sponsorship(head):
            candidate.signals["sponsor_page"] = True
            candidate.signals["sponsor_evidence"] = "feed"
        return True
