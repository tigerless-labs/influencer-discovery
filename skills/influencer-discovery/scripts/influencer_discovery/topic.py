import re
import tomllib
from functools import lru_cache

from .page import visible_text
from .paths import skill_config_dir

MAX_EVIDENCE = 8


@lru_cache(maxsize=1)
def _config():
    return tomllib.loads((skill_config_dir() / "topics.toml").read_text(encoding="utf-8"))


@lru_cache(maxsize=8)
def _pattern(subject):
    terms = sorted(_config()[subject]["terms"], key=len, reverse=True)
    joined = "|".join(re.escape(t) for t in terms)
    return re.compile(rf"(?<![\w.-])({joined})(?![\w-])", re.I)


def hits_in(text, subject="ai"):
    """The evidence is the matched terms, never the third-party text they came from."""
    if not text:
        return []
    found = []
    for match in _pattern(subject).findall(text):
        term = match.lower()
        if term not in found:
            found.append(term)
        if len(found) >= MAX_EVIDENCE:
            break
    return found


def hits_in_page(html, subject="ai"):
    return hits_in(visible_text(html), subject)


def _candidate_text(candidate):
    """Only what the person wrote. The channel's payload holds our own query, which would self-confirm."""
    parts = [candidate.display_name, candidate.bio, candidate.own_site, candidate.profile_url]
    return " \n ".join(p for p in parts if p)


def note_hits(candidate, subject="ai"):
    """Accumulates evidence on the record; callers may add page hits before judging."""
    existing = candidate.signals.get("topic_hits") or []
    for term in hits_in(_candidate_text(candidate), subject):
        if term not in existing:
            existing.append(term)
    candidate.signals["topic_hits"] = existing[:MAX_EVIDENCE]
    return candidate.signals["topic_hits"]


def is_on_topic(candidate):
    return bool(candidate.signals.get("topic_hits"))
