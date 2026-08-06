import re

from ..hop import emails_in
from ..record import Candidate, Contact
from .base import Channel, normalise_person, register

CATEGORIES = "https://substack.com/api/v1/categories"
IN_CATEGORY = "https://substack.com/api/v1/category/public/{id}/all?page={page}"
WEBMASTER = re.compile(r"<webMaster>\s*([^<]+)</webMaster>", re.I)


@register
class Newsletter(Channel):
    name = "newsletter"
    form = "directory"

    def discover(self, limit):
        wanted = {c.lower() for c in self.config.get("categories", [])}
        categories = self.fetcher.try_json(CATEGORIES) or []
        chosen = [c for c in categories if c.get("name", "").lower() in wanted] or categories[:2]

        found = []
        for category in chosen:
            page = 0
            while len(found) < limit and page < self.config.get("max_pages", 2):
                data = self.fetcher.try_json(
                    IN_CATEGORY.format(id=category.get("id"), page=page)
                )
                if not data:
                    break
                for pub in data.get("publications", []):
                    if len(found) >= limit:
                        break
                    candidate = self._to_candidate(pub, category.get("name"))
                    if candidate:
                        found.append(candidate)
                if not data.get("more"):
                    break
                page += 1
        return found

    def _to_candidate(self, pub, category):
        name = pub.get("name")
        subdomain = pub.get("subdomain")
        if not name or not subdomain:
            return None
        author = (pub.get("author_name") or "").strip()
        home = pub.get("custom_domain_optional") and pub.get("custom_domain")
        home = f"https://{pub['custom_domain']}" if pub.get("custom_domain") else None
        candidate = Candidate(
            channel=self.name,
            person_key=normalise_person(author or name),
            display_name=author or name,
            profile_url=f"https://{subdomain}.substack.com",
            own_site=home,
            payload={
                "publication": name,
                "subdomain": subdomain,
                "custom_domain": pub.get("custom_domain"),
                "author_handle": pub.get("author_handle"),
                "category": category,
                "id": pub.get("id"),
            },
        )
        self._read_feed(candidate, f"https://{subdomain}.substack.com/feed")
        return candidate

    def _read_feed(self, candidate, feed_url):
        body = self.fetcher.try_get(feed_url)
        candidate.mark_checked("feed")
        if not body:
            return
        master = WEBMASTER.search(body[:120000])
        if master:
            for address in emails_in(master.group(1)):
                candidate.add_contact(Contact(address, "email", "feed_webmaster"))
                break
