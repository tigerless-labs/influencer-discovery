import json
import re

SCRIPT_OR_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.I | re.S)
TAG = re.compile(r"<[^>]+>")
PERSON = re.compile(r'"@type"\s*:\s*"(Person|ProfilePage)"')
MAX_OBJECT = 20000


def visible_text(html):
    """Prose heuristics must never read markup: a CSS class name is not something a person wrote."""
    return TAG.sub(" ", SCRIPT_OR_STYLE.sub(" ", html or ""))


def _unescaped(text):
    for _ in range(4):
        if '\\"' not in text:
            break
        text = text.replace("\\\\", "\\").replace('\\"', '"')
    return text


def _enclosing_object(text, at):
    start = text.rfind("{", 0, at)
    if start < 0:
        return None
    depth = 0
    for i in range(start, min(len(text), start + MAX_OBJECT)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def schema_person(html, identity=None):
    """The one place a schema.org Person is read off a page, escaped payload or plain script tag.

    A profile page also carries the platform's own people. Passing the handle the page was
    fetched for turns a wrong match into no match, which is the only safe direction.
    """
    text = _unescaped(html or "")
    people = []
    for match in PERSON.finditer(text):
        found = _enclosing_object(text, match.start())
        if not isinstance(found, dict):
            continue
        profile_page = found.get("@type") == "ProfilePage"
        person = found.get("mainEntity") if profile_page else found
        if isinstance(person, dict) and person.get("name"):
            people.append((0 if profile_page else 1, person))
    if not people:
        return None
    if identity:
        wanted = identity.lower()
        for _, person in sorted(people, key=lambda pair: pair[0]):
            named = f"{person.get('alternateName') or ''} {person.get('url') or ''}".lower()
            if wanted in named:
                return person
        return None
    return min(people, key=lambda pair: pair[0])[1]
