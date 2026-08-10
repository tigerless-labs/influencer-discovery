from collections import Counter

from .paths import memory_dir
from .record import Outcome

ZH = {
    Outcome.QUALIFIED: "qualified",
    Outcome.NO_CONTACT: "no contact",
    Outcome.BUYER: "buyer, kept off the sheet",
    Outcome.AUDIENCE_OUT_OF_BAND: "audience out of band",
    Outcome.AUDIENCE_UNVERIFIED: "audience unverified",
    Outcome.OFF_TOPIC: "off topic",
}


class Report:
    def __init__(self, run_id, ask):
        self.run_id = run_id
        self.ask = ask
        self.channels = {}
        self.notes = []

    def add(self, channel, candidates, stop_reason, planned, note=None, shortfall=None):
        self.channels[channel] = {
            "planned": planned,
            "crawled": len(candidates),
            "outcomes": Counter(c.outcome for c in candidates),
            "qualified": [c for c in candidates if c.outcome is Outcome.QUALIFIED],
            "unverified": [c for c in candidates if c.outcome is Outcome.AUDIENCE_UNVERIFIED],
            "stop": stop_reason,
            "shortfall": shortfall,
            "note": note,
        }

    def note(self, text):
        self.notes.append(text)

    def _summary_table(self):
        lines = [
            "| Channel | Target (qualified) | Judged | Qualified | Stop reason | Shortfall |",
            "|---|---|---|---|---|---|",
        ]
        for name, block in self.channels.items():
            lines.append(
                f"| {name} | {block['planned']} | {block['crawled']} "
                f"| {len(block['qualified'])} | {block['stop']} | {block.get('shortfall') or '—'} |"
            )
        return "\n".join(lines)

    def _outcome_table(self):
        lines = ["| Channel | " + " | ".join(ZH[o] for o in Outcome) + " |"]
        lines.append("|" + "---|" * (len(Outcome) + 1))
        for name, block in self.channels.items():
            counts = [str(block["outcomes"].get(o, 0)) for o in Outcome]
            lines.append(f"| {name} | " + " | ".join(counts) + " |")
        return "\n".join(lines)

    def _contactable(self):
        blocks = []
        for name, block in self.channels.items():
            if not block["qualified"]:
                continue
            rows = ["| Name | Email | Source | Followers | In band | Topic evidence | Site |",
                    "|---|---|---|---|---|---|---|"]
            for c in block["qualified"]:
                source = next((x.source for x in c.contacts if x.kind == "email"), "")
                audience = f"{c.audience.value:,}" if c.audience and c.audience.value else "unknown"
                in_band = {True: "✅", False: "out of band", None: "—"}[c.signals.get("in_band")]
                evidence = ", ".join((c.signals.get("topic_hits") or [])[:4])
                rows.append(
                    f"| {c.display_name} | {c.email} | {source} | {audience} | {in_band} "
                    f"| {evidence} | {c.own_site or c.profile_url or ''} |"
                )
            blocks.append(f"### {name}\n\n" + "\n".join(rows))
        return "\n\n".join(blocks) or "No qualified rows this run."

    def _review_queue(self):
        blocks = []
        for name, block in self.channels.items():
            if not block["unverified"]:
                continue
            rows = ["| Name | Email | Source | Site |", "|---|---|---|---|"]
            for c in block["unverified"]:
                source = next((x.source for x in c.contacts if x.kind == "email"), "")
                rows.append(
                    f"| {c.display_name} | {c.email} | {source} | {c.own_site or c.profile_url or ''} |"
                )
            blocks.append(f"### {name}\n\n" + "\n".join(rows))
        return "\n\n".join(blocks)

    def render(self):
        total = sum(len(b["qualified"]) for b in self.channels.values())
        parts = [
            f"# Run report {self.run_id}",
            "",
            "## Three things about this run",
            "",
            f"- **How many** — **{self.ask['total']} qualified rows in total** (across channels), at most {self.ask['per_channel']} per channel.",
            f"- **What counts** — **{self.ask['subject'].upper()}-relevant** with a reachable contact. "
            "Topic is the gate; a missing follower count does not disqualify.",
            f"- **What ranks first** — followers {self.ask['band'][0]:,}–{self.ask['band'][1]:,} come first, then anyone with a number, then unknown sizes.",
            "",
            "## Planned vs actual",
            "",
            self._summary_table(),
            "",
            f"**{total}** qualified rows in total.",
            "",
            "## Verdict distribution",
            "",
            self._outcome_table(),
            "",
            "## Contactable list (by channel)",
            "",
            self._contactable(),
        ]
        queue = self._review_queue()
        if queue:
            parts += [
                "",
                "## For review — has an email, size unverifiable",
                "",
                "**These do not go to the target sheet.** The platform exposes no follower count "
                "and the site shows no sponsorship evidence — whether the size is in band cannot "
                "be judged, but the person is real.",
                "",
                queue,
            ]
        if self.notes:
            parts += ["", "## Deviations and notes", ""] + [f"- {n}" for n in self.notes]
        return "\n".join(parts) + "\n"

    def save(self):
        directory = memory_dir()
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self.run_id}.md"
        suffix = 2
        while path.exists():
            path = directory / f"{self.run_id}-{suffix}.md"
            suffix += 1
        path.write_text(self.render(), encoding="utf-8")
        return path
