from ..record import Candidate
from .base import Channel, register

DISCOVER = "https://micro.blog/posts/discover"


@register
class MicroBlog(Channel):
    name = "microblog"
    form = "directory"

    def discover(self, limit):
        feed = self.fetcher.try_json(DISCOVER) or {}
        found = {}
        for item in feed.get("items", []):
            if len(found) >= limit:
                break
            author = item.get("author") or {}
            handle = (author.get("_microblog") or {}).get("username") or author.get("name")
            site = author.get("url")
            if not handle or handle in found:
                continue
            if not site or "micro.blog" in site:
                continue
            found[handle] = Candidate(
                channel=self.name,
                person_key=handle,
                display_name=author.get("name") or handle,
                profile_url=f"https://micro.blog/{handle}",
                own_site=site,
                payload={"post_url": item.get("url"), "published": item.get("date_published")},
            )
        return list(found.values())
