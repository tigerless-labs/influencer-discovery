from dataclasses import dataclass

from .record import Outcome

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
    def __init__(self, band):
        self.low, self.high = band

    def judge(self, candidate):
        if not candidate.contacts:
            return Verdict(Outcome.NO_CONTACT, False, "no reachable address")

        if candidate.signals.get("is_buyer"):
            return Verdict(Outcome.BUYER, False, candidate.signals.get("buyer_reason", "product site"))

        audience = candidate.audience
        if audience and audience.unit == BAND_UNIT:
            if self.low <= audience.value <= self.high:
                return Verdict(Outcome.QUALIFIED, True, f"{audience.value} {audience.unit}")
            return Verdict(
                Outcome.AUDIENCE_OUT_OF_BAND, True, f"{audience.value} {audience.unit}"
            )

        if candidate.signals.get("sponsor_page"):
            return Verdict(Outcome.QUALIFIED, False, "sponsorship page on own site")

        return Verdict(Outcome.AUDIENCE_UNVERIFIED, False, "contactable, but neither a follower count nor sponsorship evidence")
