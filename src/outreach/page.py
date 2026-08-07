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


def schema_person(html):
    """The one place a schema.org Person is read off a page, escaped payload or plain script tag."""
    text = _unescaped(html or "")
    for match in PERSON.finditer(text):
        found = _enclosing_object(text, match.start())
        if not isinstance(found, dict):
            continue
        person = found.get("mainEntity") if found.get("@type") == "ProfilePage" else found
        if isinstance(person, dict) and person.get("name"):
            return person
    return None
