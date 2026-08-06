from dataclasses import dataclass, field
from enum import Enum

CONTACT_KINDS = {"email", "form"}


class Outcome(Enum):
    QUALIFIED = "qualified"
    NO_CONTACT = "no_contact"
    BUYER = "buyer"
    AUDIENCE_OUT_OF_BAND = "audience_out_of_band"
    AUDIENCE_UNVERIFIED = "audience_unverified"


@dataclass
class Audience:
    value: int
    unit: str
    as_of: str

    def compare(self, other):
        if self.unit != other.unit:
            raise TypeError(f"{self.unit} and {other.unit} are not comparable")
        return (self.value > other.value) - (self.value < other.value)

    def to_row(self):
        return {"value": self.value, "unit": self.unit, "as_of": self.as_of}

    @classmethod
    def from_row(cls, row):
        return cls(**row) if row else None


@dataclass
class Contact:
    value: str
    kind: str
    source: str

    def __post_init__(self):
        if not self.source:
            raise ValueError("a contact without a source cannot be judged later")
        if self.kind not in CONTACT_KINDS:
            raise ValueError(f"unknown contact kind: {self.kind}")

    def to_row(self):
        return {"value": self.value, "kind": self.kind, "source": self.source}


@dataclass
class Candidate:
    channel: str
    person_key: str
    display_name: str
    profile_url: str = None
    own_site: str = None
    audience: Audience = None
    bio: str = None
    contacts: list = field(default_factory=list)
    signals: dict = field(default_factory=dict)
    payload: dict = field(default_factory=dict)
    checked: list = field(default_factory=list)
    outcome: Outcome = None
    run_id: str = None
    seen_at: str = None

    @property
    def dedup_key(self):
        return (self.person_key, self.channel)

    @property
    def email(self):
        return next((c.value for c in self.contacts if c.kind == "email"), None)

    def add_contact(self, contact):
        if contact.value.lower() not in {c.value.lower() for c in self.contacts}:
            self.contacts.append(contact)

    def mark_checked(self, what):
        if what not in self.checked:
            self.checked.append(what)

    def was_checked(self, what):
        return what in self.checked

    def to_row(self):
        return {
            "channel": self.channel,
            "person_key": self.person_key,
            "display_name": self.display_name,
            "profile_url": self.profile_url,
            "own_site": self.own_site,
            "audience": self.audience.to_row() if self.audience else None,
            "bio": self.bio,
            "contacts": [c.to_row() for c in self.contacts],
            "signals": self.signals,
            "payload": self.payload,
            "checked": self.checked,
            "outcome": self.outcome.value if self.outcome else None,
            "run_id": self.run_id,
            "seen_at": self.seen_at,
        }

    @classmethod
    def from_row(cls, row):
        row = dict(row)
        row["audience"] = Audience.from_row(row.get("audience"))
        row["contacts"] = [Contact(**c) for c in row.get("contacts") or []]
        row["outcome"] = Outcome(row["outcome"]) if row.get("outcome") else None
        return cls(**row)
