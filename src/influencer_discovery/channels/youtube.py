import json
import re
import urllib.parse

from ..hop import emails_in
from ..record import Audience, Candidate, Contact
from ..topic import note_hits
from .base import Channel, register

SEARCH = "https://www.youtube.com/results?search_query={q}&sp=EgIQAg%253D%253D"
ABOUT = "https://www.youtube.com/{handle}/about"
INITIAL_DATA = re.compile(r"ytInitialData\s*=\s*(\{.*?\});</script>", re.S)
REDIRECT = re.compile(r"/redirect\?[^\"']*?q=([^\"'&]+)")
SUBSCRIBERS = re.compile(r"([\d.,]+)\s*([KMB]?)\s*subscribers", re.I)
CHANNEL_TITLE = re.compile(r'"channelMetadataRenderer":\{"title":"((?:[^"\\]|\\.)*)"')
OG_TITLE = re.compile(r'<meta property="og:title" content="([^"]+)"')
MULTIPLIER = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}


def _initial_data(html):
    match = INITIAL_DATA.search(html or "")
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def _walk(node, key):
    """The result shape shifts between renderers, so the handle is found by key, not by path."""
    if isinstance(node, dict):
        if key in node:
            yield node[key]
        for value in node.values():
            yield from _walk(value, key)
    elif isinstance(node, list):
        for item in node:
            yield from _walk(item, key)


def subscribers_from(text):
    match = SUBSCRIBERS.search(text or "")
    if not match:
        return None
    try:
        return int(float(match.group(1).replace(",", "")) * MULTIPLIER[match.group(2).upper()])
    except (ValueError, KeyError):
        return None


@register
class YouTube(Channel):
    name = "youtube"
    form = "search"
    audience_unit = "followers"

    def discover(self, limit):
        handles = []
        for term in self.config.get("terms", []):
            if len(handles) >= limit:
                break
            html = self.fetcher.try_get(SEARCH.format(q=urllib.parse.quote(term)))
            if not html:
                continue
            for handle in self._handles(html):
                if handle not in handles and not self.already_have(handle):
                    handles.append(handle)

        found = []
        for handle in handles:
            if len(found) >= limit:
                break
            candidate = self._about(handle)
            if candidate and note_hits(candidate):
                found.append(candidate)
        return found

    @staticmethod
    def _handles(html):
        seen = []
        for url in _walk(_initial_data(html), "canonicalBaseUrl"):
            if isinstance(url, str) and url.startswith("/@") and url not in seen:
                seen.append(url.lstrip("/"))
        for url in re.findall(r'"canonicalBaseUrl":"(/@[\w.\-]+)"', html):
            if url.lstrip("/") not in seen:
                seen.append(url.lstrip("/"))
        return seen

    @staticmethod
    def _channel_name(html):
        """Walking for "title" finds the tab labels first; the channel name has its own key."""
        match = CHANNEL_TITLE.search(html or "") or OG_TITLE.search(html or "")
        if not match:
            return None
        try:
            return json.loads(f'"{match.group(1)}"')
        except json.JSONDecodeError:
            return match.group(1)

    def _about(self, handle):
        """The description and the link panel are both in the first HTML; no key, no browser."""
        html = self.fetcher.try_get(ABOUT.format(handle=urllib.parse.quote(handle)))
        if not html:
            return None
        data = _initial_data(html)
        description = next(
            (d for d in _walk(data, "description") if isinstance(d, str) and len(d) > 20), ""
        )
        title = self._channel_name(html) or handle
        links = [urllib.parse.unquote(u) for u in REDIRECT.findall(html)]
        subscribers = subscribers_from(html)

        candidate = Candidate(
            channel=self.name,
            person_key=handle.lstrip("@"),
            display_name=title,
            profile_url=f"https://www.youtube.com/{handle}",
            own_site=links[0] if links else None,
            audience=Audience(subscribers, self.audience_unit, "2026-08-07") if subscribers else None,
            bio=description,
            payload={"handle": handle, "links": links[:6]},
        )
        for address in emails_in(description):
            candidate.add_contact(Contact(address, "email", "platform_bio"))
            break
        candidate.mark_checked("about")
        return candidate
