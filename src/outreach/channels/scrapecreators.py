from ..paths import credential

BASE = "https://api.scrapecreators.com"


class OutOfCredits(Exception):
    pass


class ScrapeCreators:
    """The only metered egress. It holds the budget so a dry account cannot burn a run on 402s."""

    def __init__(self, fetcher, budget):
        self.fetcher = fetcher
        self.remaining = budget
        self.key = credential("SCRAPECREATORS_API_KEY")
        self.balance = None

    @property
    def available(self):
        return bool(self.key) and self.remaining > 0 and self.balance != 0

    def call(self, path, **params):
        if not self.available:
            raise OutOfCredits(f"no budget left before {path}")
        query = "&".join(f"{k}={v}" for k, v in params.items())
        data = self.fetcher.try_json(f"{BASE}/{path}?{query}", headers={"x-api-key": self.key})
        if data is None:
            return None
        if "credits_remaining" in data:
            self.balance = data["credits_remaining"]
        if data.get("success") is False:
            return None
        self.remaining -= data.get("credits_charged", 0) or 0
        return data
