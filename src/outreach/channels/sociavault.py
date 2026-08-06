from ..paths import credential

BASE = "https://api.sociavault.com/v1/scrape"
CREDITS = "https://api.sociavault.com/v1/credits"


class OutOfCredits(Exception):
    pass


class SociaVault:
    """Metered egress. Every call that returns data costs one credit, so the budget is held here."""

    def __init__(self, fetcher, budget):
        self.fetcher = fetcher
        self.remaining = budget
        self.key = credential("SOCIAVAULT_API_KEY")

    @property
    def available(self):
        return bool(self.key) and self.remaining > 0

    def balance(self):
        data = self.fetcher.try_json(CREDITS, headers={"X-API-Key": self.key})
        return (data or {}).get("credits")

    def call(self, path, **params):
        if not self.available:
            raise OutOfCredits(f"budget exhausted before {path}")
        query = "&".join(f"{k}={v}" for k, v in params.items())
        data = self.fetcher.try_json(f"{BASE}/{path}?{query}", headers={"X-API-Key": self.key})
        if data is None:
            return None
        self.remaining -= 1
        if data.get("success") is False:
            return None
        return self.unwrap(data)

    @staticmethod
    def unwrap(data):
        """The payload arrives inside a variable number of {success, data: ...} envelopes."""
        while isinstance(data, dict) and isinstance(data.get("data"), dict):
            data = data["data"]
        return data
