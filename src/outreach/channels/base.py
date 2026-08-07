import re

REGISTRY = {}


def register(cls):
    REGISTRY[cls.name] = cls
    return cls


def normalise_person(text):
    text = re.sub(r"\s+", " ", (text or "").strip().lower())
    return re.sub(r"[^\w \-.@]", "", text)


class Channel:
    """A channel owns its own discovery and its own payload shape. Nothing else may read that payload."""

    name = None
    form = "search"
    audience_unit = None

    def __init__(self, fetcher, config=None):
        self.fetcher = fetcher
        self.config = config or {}

    def already_have(self, person_key):
        """A directory channel that cannot skip what it has seen never gets past its first page."""
        return False

    def discover(self, limit):
        raise NotImplementedError

    def stop_reason(self):
        return "凑够" if self.form == "search" else "翻到底"
