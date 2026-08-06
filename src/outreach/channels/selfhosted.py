from ..domains import is_a_persons_own_site
from ..hop import registrable_domain
from ..record import Candidate
from .base import Channel, register

HN = "https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage=200"
LOBSTERS = "https://lobste.rs/hottest.json"



@register
class SelfHosted(Channel):
    name = "blog"
    form = "search"

    def discover(self, limit):
        found = {}
        for url, extract in ((HN, self._hn), (LOBSTERS, self._lobsters)):
            data = self.fetcher.try_json(url)
            if not data:
                continue
            for title, link in extract(data):
                if len(found) >= limit:
                    break
                domain = registrable_domain(link)
                if not domain or domain in found or not is_a_persons_own_site(link):
                    continue
                found[domain] = Candidate(
                    channel=self.name,
                    person_key=domain,
                    display_name=domain,
                    profile_url=link,
                    own_site=f"https://{domain}",
                    payload={"discovered_via": url.split("/")[2], "title": title, "post": link},
                )
        return list(found.values())[:limit]

    @staticmethod
    def _hn(data):
        for hit in data.get("hits", []):
            if hit.get("url"):
                yield hit.get("title"), hit["url"]

    @staticmethod
    def _lobsters(data):
        for story in data:
            if story.get("url"):
                yield story.get("title"), story["url"]
