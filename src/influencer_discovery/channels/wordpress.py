from ..record import Candidate, Contact
from .base import Channel, register

TAG_POSTS = "https://public-api.wordpress.com/rest/v1.2/read/tags/{tag}/posts?number=40"
GRAVATAR = "https://gravatar.com/{name}.json"


@register
class WordPressCom(Channel):
    name = "wordpress"
    form = "search"

    def discover(self, limit):
        found = {}
        for tag in self.config.get("tags", []):
            if len(found) >= limit:
                break
            data = self.fetcher.try_json(TAG_POSTS.format(tag=tag))
            for post in (data or {}).get("posts", []):
                if len(found) >= limit:
                    break
                author = post.get("author") or {}
                nice = author.get("nice_name")
                if not nice or nice in found:
                    continue
                candidate = Candidate(
                    channel=self.name,
                    person_key=nice,
                    display_name=author.get("name") or nice,
                    profile_url=author.get("profile_URL"),
                    own_site=author.get("URL") or post.get("site_URL"),
                    payload={
                        "tag": tag,
                        "site_URL": post.get("site_URL"),
                        "site_name": post.get("site_name"),
                        "post_date": post.get("date"),
                    },
                )
                self._gravatar(candidate, nice)
                found[nice] = candidate
        return list(found.values())[:limit]

    def _gravatar(self, candidate, nice_name):
        data = self.fetcher.try_json(GRAVATAR.format(name=nice_name))
        candidate.mark_checked("gravatar")
        entries = (data or {}).get("entry") or []
        for entry in entries:
            for record in entry.get("emails") or []:
                if record.get("value"):
                    candidate.add_contact(Contact(record["value"], "email", "gravatar_public"))
                    return
