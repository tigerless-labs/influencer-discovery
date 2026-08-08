from dataclasses import dataclass

from .record import Outcome
from .topic import is_on_topic, note_hits

BAND_UNIT = "followers"


@dataclass
class Verdict:
    outcome: Outcome
    band_applied: bool
    reason: str

    @property
    def writes_to_sheet(self):
        return self.outcome is Outcome.QUALIFIED


class Gate:
    """Reachable, on topic, and not a buyer. Audience size orders the result; it does not reject."""

    def __init__(self, band, subject="ai", floor=0):
        self.low, self.high = band
        self.subject = subject
        self.floor = floor

    def _measured(self, candidate):
        audience = candidate.audience
        return audience if audience and audience.unit == BAND_UNIT and audience.value else None

    def too_small(self, candidate):
        """Answerable the moment a size is known, so the walk is never paid for below the floor."""
        audience = self._measured(candidate)
        return bool(self.floor and audience and audience.value < self.floor)

    def judge(self, candidate):
        if self.too_small(candidate):
            candidate.signals["in_band"] = False
            return Verdict(
                Outcome.AUDIENCE_OUT_OF_BAND, True,
                f"{candidate.audience.value} {candidate.audience.unit} < {self.floor}",
            )

        if not candidate.contacts:
            return Verdict(Outcome.NO_CONTACT, False, "no reachable address")

        if candidate.signals.get("is_buyer"):
            return Verdict(Outcome.BUYER, False, candidate.signals.get("buyer_reason", "product site"))

        note_hits(candidate, self.subject)
        if not is_on_topic(candidate):
            return Verdict(Outcome.OFF_TOPIC, False, f"no {self.subject} evidence anywhere")

        audience = self._measured(candidate)
        measured = audience is not None
        candidate.signals["in_band"] = (
            self.low <= audience.value <= self.high if measured else None
        )
        evidence = ", ".join(candidate.signals.get("topic_hits") or [])
        size = f"{audience.value} {audience.unit}" if measured else "规模未知"
        return Verdict(Outcome.QUALIFIED, measured, f"{size};{evidence}")

    def rank(self, candidates):
        """In-band first, then any measured size, then the rest. Unknown size never sinks below off-band."""
        def key(c):
            in_band = c.signals.get("in_band")
            value = c.audience.value if c.audience and c.audience.value else 0
            tier = 0 if in_band is True else (1 if in_band is None else 2)
            return (tier, -value)

        return sorted(candidates, key=key)
