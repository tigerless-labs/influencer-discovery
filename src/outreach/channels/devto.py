from ..record import Audience, Candidate
from .base import Channel, register

ARTICLES = "https://dev.to/api/articles?tag={tag}&per_page=100&top=365"


@register
class DevTo(Channel):
    name = "devto"
    form = "search"
    audience_unit = "reactions"

    def discover(self, limit):
        found = {}
        for tag in self.config.get("tags", []):
            if len(found) >= limit:
                break
            for article in self.fetcher.try_json(ARTICLES.format(tag=tag)) or []:
                if len(found) >= limit:
                    break
                user = article.get("user") or {}
                username = user.get("username")
                if not username or username in found:
                    continue
                canonical = article.get("canonical_url") or ""
                off_site = bool(canonical) and "dev.to/" not in canonical
                if not off_site and not user.get("website_url"):
                    continue
                found[username] = Candidate(
                    channel=self.name,
                    person_key=username,
                    display_name=user.get("name") or username,
                    profile_url=f"https://dev.to/{username}",
                    own_site=user.get("website_url") or (canonical if off_site else None),
                    audience=Audience(
                        value=article.get("public_reactions_count") or 0,
                        unit=self.audience_unit,
                        as_of=article.get("published_at", "")[:10],
                    ),
                    payload={
                        "tag": tag,
                        "canonical_url": canonical,
                        "off_site_canonical": off_site,
                        "github_username": user.get("github_username"),
                        "twitter_username": user.get("twitter_username"),
                        "title": article.get("title"),
                    },
                )
        ordered = sorted(
            found.values(),
            key=lambda c: (not c.payload["off_site_canonical"], -(c.audience.value if c.audience else 0)),
        )
        return ordered[:limit]
