import re

from ..domains import is_a_persons_own_site
from ..hop import emails_in
from ..page import schema_person
from ..record import Candidate, Contact
from .base import Channel, register

SITEMAP = "https://www.freecodecamp.org/news/sitemap-authors.xml"
AUTHOR = "https://www.freecodecamp.org/news/author/{slug}/"
SLUG = re.compile(r"<loc>\s*https://www\.freecodecamp\.org/news/author/([^/<\s]+)/?\s*</loc>")


@register
class FreeCodeCamp(Channel):
    name = "freecodecamp"
    form = "directory"

    def discover(self, limit):
        slugs = SLUG.findall(self.fetcher.try_get(SITEMAP) or "")
        candidates = []
        for slug in slugs:
            if len(candidates) >= limit:
                break
            candidate = self._author(slug)
            if candidate:
                candidates.append(candidate)
        return candidates

    def _author(self, slug):
        page = self.fetcher.try_get(AUTHOR.format(slug=slug))
        person = schema_person(page) if page else None
        if not person:
            return None
        bio = person.get("description") or ""
        links = [
            link
            for link in person.get("sameAs") or []
            if isinstance(link, str) and link.startswith(("http://", "https://"))
        ]
        candidate = Candidate(
            channel=self.name,
            person_key=slug,
            display_name=person.get("name") or slug,
            profile_url=AUTHOR.format(slug=slug),
            own_site=next((link for link in links if is_a_persons_own_site(link)), None),
            bio=bio,
            payload={"same_as": links},
        )
        for address in emails_in(bio):
            candidate.add_contact(Contact(address, "email", "platform_bio"))
            break
        candidate.mark_checked("profile")
        return candidate
