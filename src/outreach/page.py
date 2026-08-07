import re

SCRIPT_OR_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.I | re.S)
TAG = re.compile(r"<[^>]+>")


def visible_text(html):
    """Prose heuristics must never read markup: a CSS class name is not something a person wrote."""
    return TAG.sub(" ", SCRIPT_OR_STYLE.sub(" ", html or ""))
