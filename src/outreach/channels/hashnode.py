import html
import re

from ..domains import is_a_persons_own_site
from ..hop import emails_in
from ..page import schema_person
from ..record import Candidate, Contact
from .base import Channel, register

TAG = "https://hashnode.com/n/{tag}"
PROFILE = "https://hashnode.com/@{handle}"
HANDLE = re.compile(r'href="/@([A-Za-z0-9_\-]+)"')
BIO = re.compile(r'<meta property="og:description" content="([^"]*)"')
TITLE = re.compile(r'<meta property="og:title" content="([^"]*)"')
URL = re.compile(r"https?://[^\s\"'<>)]+")


@register
class Hashnode(Channel):
    name = "hashnode"
    form = "search"

    def discover(self, limit):
        handles = []
        for tag in self.config.get("tags", []):
            if len(handles) >= limit:
                break
            page = self.fetcher.try_get(TAG.format(tag=tag))
            for handle in HANDLE.findall(page or ""):
                if handle not in handles:
                    handles.append(handle)

        candidates = []
        for handle in handles[:limit]:
            candidate = self._profile(handle)
            if candidate and candidate.own_site:
                candidates.append(candidate)
        return candidates

    def _profile(self, handle):
        page = self.fetcher.try_get(PROFILE.format(handle=handle))
        if not page:
            return None
        person = schema_person(page) or {}
        found = BIO.search(page)
        bio = html.unescape(html.unescape(found.group(1))) if found else ""
        titled = TITLE.search(page)
        billed = html.unescape(titled.group(1)).split(" (@")[0].strip() if titled else ""
        links = [
            link
            for link in (person.get("sameAs") or [])
            if isinstance(link, str) and link.startswith(("http://", "https://"))
        ] + URL.findall(bio)
        candidate = Candidate(
            channel=self.name,
            person_key=handle,
            display_name=person.get("name") or billed or handle,
            profile_url=PROFILE.format(handle=handle),
            own_site=next((link for link in links if is_a_persons_own_site(link)), None),
            bio=bio,
            payload={"blog": f"https://{handle}.hashnode.dev", "same_as": links},
        )
        for address in emails_in(bio):
            candidate.add_contact(Contact(address, "email", "platform_bio"))
            break
        candidate.mark_checked("profile")
        return candidate
