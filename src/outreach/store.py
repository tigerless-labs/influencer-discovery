import json
from datetime import datetime, timezone
from pathlib import Path

from .record import Candidate
from .paths import state_dir


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug(text):
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in text.lower())


class Store:
    def __init__(self, root=None):
        self.root = Path(root) if root else state_dir()
        self.seen_dir = self.root / "seen"
        self.sites_file = self.root / "sites.jsonl"
        self.failures_file = self.root / "failures.jsonl"
        self.seen_dir.mkdir(parents=True, exist_ok=True)

    def _channel_file(self, channel):
        return self.seen_dir / f"{_slug(channel)}.jsonl"

    @staticmethod
    def _append(path, row):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    @staticmethod
    def _read(path):
        if not path.exists():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue

    def record(self, candidate, run_id=None):
        candidate.run_id = run_id or candidate.run_id
        candidate.seen_at = _now()
        self._append(self._channel_file(candidate.channel), candidate.to_row())
        return candidate

    def record_site(self, domain, outcome, run_id=None):
        self._append(
            self.sites_file,
            {"domain": domain, "outcome": outcome, "run_id": run_id, "seen_at": _now()},
        )

    def record_failure(self, url, reason, run_id=None):
        self._append(
            self.failures_file,
            {"url": url, "reason": reason, "run_id": run_id, "at": _now()},
        )

    def raw_lines(self, channel):
        path = self._channel_file(channel)
        return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    def people(self, channel=None):
        files = [self._channel_file(channel)] if channel else sorted(self.seen_dir.glob("*.jsonl"))
        latest = {}
        for path in files:
            for row in self._read(path):
                latest[(row.get("person_key"), row.get("channel"))] = row
        for row in latest.values():
            try:
                yield Candidate.from_row(row)
            except (TypeError, ValueError):
                continue

    def seen_keys(self):
        return {
            (row.get("person_key"), row.get("channel"))
            for path in self.seen_dir.glob("*.jsonl")
            for row in self._read(path)
        }

    def is_seen(self, key):
        person, channel = key
        return any(
            row.get("person_key") == person
            for row in self._read(self._channel_file(channel))
        )

    def seen_sites(self):
        return {row.get("domain") for row in self._read(self.sites_file)}

    def is_site_seen(self, domain):
        return domain in self.seen_sites()

    def failures(self):
        return list(self._read(self.failures_file))

    def seed(self, name_platform_pairs, run_id="seed"):
        for name, platform in name_platform_pairs:
            if not name or not platform:
                continue
            key = (name.strip().lower(), platform.strip().lower())
            if self.is_seen(key):
                continue
            self._append(
                self._channel_file(key[1]),
                {
                    "channel": key[1],
                    "person_key": key[0],
                    "display_name": name.strip(),
                    "outcome": None,
                    "signals": {"seeded_from_sheet": True},
                    "run_id": run_id,
                    "seen_at": _now(),
                },
            )
