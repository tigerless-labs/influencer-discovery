from .buyer import looks_like_a_product_site
from .domains import (
    is_a_persons_own_site,
    is_link_aggregator,
    looks_like_a_multi_author_publication,
    registrable_domain,
)
from .hop import (
    emails_in,
    external_links,
    internal_links,
    is_directory_page,
    looks_contactish,
    looks_like_sponsor_page,
    mailto_addresses,
    mentions_sponsorship,
)
from .record import Contact
from .topic import hits_in_page

MAX_SUBPAGES = 5


class SecondHop:
    """Platform page -> the person's own site -> their contact page."""

    def __init__(self, fetcher, store=None, run_id=None):
        self.fetcher = fetcher
        self.store = store
        self.run_id = run_id

    def walk(self, candidate):
        site = candidate.own_site
        candidate.mark_checked("own_site")
        if not site:
            return candidate
        if is_link_aggregator(site):
            site = self._through_aggregator(candidate, site)
            if not site:
                return candidate
        if not is_a_persons_own_site(site):
            candidate.signals["own_site_is_a_platform"] = True
            return candidate
        domain = registrable_domain(site)
        if not domain:
            return candidate

        root = self.fetcher.try_get(site)
        candidate.mark_checked("site_root")
        if root is None:
            return candidate

        if looks_like_a_product_site(root):
            candidate.signals["is_buyer"] = True
            candidate.signals["buyer_reason"] = "landing page sells a product, no audience surface"
        if looks_like_a_multi_author_publication(root):
            candidate.signals["is_buyer"] = True
            candidate.signals["buyer_reason"] = "multi-author publication, not a reachable person"

        self._note_topic(candidate, root)
        self._harvest(candidate, root, "site_root")
        links = internal_links(root, site)
        sponsor_links = [u for u in links if looks_like_sponsor_page(u)]
        candidate.signals["sponsor_page"] = bool(sponsor_links) or mentions_sponsorship(root)

        targets = sponsor_links[:2] + [u for u in links if looks_contactish(u)]
        seen = set()
        for url in targets:
            if len(seen) >= MAX_SUBPAGES:
                break
            if url in seen:
                continue
            seen.add(url)
            page = self.fetcher.try_get(url)
            if page is None:
                continue
            source = "sponsor_page" if looks_like_sponsor_page(url) else "site_contact"
            self._note_topic(candidate, page)
            self._harvest(candidate, page, source)

        candidate.mark_checked("site_contact")
        if self.store:
            self.store.record_site(
                domain,
                "found" if candidate.email else "no_contact",
                run_id=self.run_id,
            )
        return candidate

    def _through_aggregator(self, candidate, url):
        """A link page is a redirect with extra steps: read it, take the first real site, keep going."""
        candidate.signals["via_aggregator"] = url
        page = self.fetcher.try_get(url)
        candidate.mark_checked("aggregator")
        if page is None:
            return None
        self._note_topic(candidate, page)
        self._harvest(candidate, page, "aggregator_page")
        for link in external_links(page, url):
            if is_a_persons_own_site(link):
                candidate.own_site = link
                return link
        return None

    def _note_topic(self, candidate, html):
        existing = candidate.signals.get("topic_hits") or []
        for term in hits_in_page(html):
            if term not in existing:
                existing.append(term)
        candidate.signals["topic_hits"] = existing[:8]

    def _harvest(self, candidate, html, source):
        addresses = mailto_addresses(html) or emails_in(html)
        if not addresses or is_directory_page(addresses):
            return
        site_domain = registrable_domain(candidate.own_site)
        addresses.sort(key=lambda a: a.rpartition("@")[2] != site_domain)
        candidate.add_contact(Contact(addresses[0], "email", source))
