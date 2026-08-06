from collections import Counter

from .paths import memory_dir
from .record import Outcome

ZH = {
    Outcome.QUALIFIED: "合格",
    Outcome.NO_CONTACT: "无联系方式",
    Outcome.BUYER: "买方,不进表",
    Outcome.AUDIENCE_OUT_OF_BAND: "规模不在带内",
    Outcome.AUDIENCE_UNVERIFIED: "规模未核实",
}


class Report:
    def __init__(self, run_id, ask):
        self.run_id = run_id
        self.ask = ask
        self.channels = {}
        self.notes = []

    def add(self, channel, candidates, stop_reason, planned, note=None):
        self.channels[channel] = {
            "planned": planned,
            "crawled": len(candidates),
            "outcomes": Counter(c.outcome for c in candidates),
            "qualified": [c for c in candidates if c.outcome is Outcome.QUALIFIED],
            "unverified": [c for c in candidates if c.outcome is Outcome.AUDIENCE_UNVERIFIED],
            "stop": stop_reason,
            "note": note,
        }

    def note(self, text):
        self.notes.append(text)

    def _summary_table(self):
        lines = ["| 渠道 | 计划 | 实际抓取 | 合格 | 停止原因 |", "|---|---|---|---|---|"]
        for name, block in self.channels.items():
            lines.append(
                f"| {name} | {block['planned']} | {block['crawled']} "
                f"| {len(block['qualified'])} | {block['stop']} |"
            )
        return "\n".join(lines)

    def _outcome_table(self):
        lines = ["| 渠道 | " + " | ".join(ZH[o] for o in Outcome) + " |"]
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
            rows = ["| 名字 | 邮箱 | 来源 | 受众 | 站点 |", "|---|---|---|---|---|"]
            for c in block["qualified"]:
                source = next((x.source for x in c.contacts if x.kind == "email"), "")
                audience = f"{c.audience.value} {c.audience.unit}" if c.audience else "—"
                rows.append(
                    f"| {c.display_name} | {c.email} | {source} | {audience} "
                    f"| {c.own_site or c.profile_url or ''} |"
                )
            blocks.append(f"### {name}\n\n" + "\n".join(rows))
        return "\n\n".join(blocks) or "本轮没有合格行。"

    def _review_queue(self):
        blocks = []
        for name, block in self.channels.items():
            if not block["unverified"]:
                continue
            rows = ["| 名字 | 邮箱 | 来源 | 站点 |", "|---|---|---|---|"]
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
            f"# 运行报告 {self.run_id}",
            "",
            "## 本轮的三件事",
            "",
            f"- **要多少** —— {self.ask['per_channel']} 条 / 渠道,YouTube 除外。",
            f"- **符合要求** —— 粉丝数 {self.ask['band'][0]}–{self.ask['band'][1]};"
            "平台不给粉丝数的渠道改判自有站上有没有招商页。",
            f"- **优先什么** —— {self.ask['priority']}。",
            "",
            "## 计划与实际",
            "",
            self._summary_table(),
            "",
            f"合格合计 **{total}** 条。",
            "",
            "## 判定分布",
            "",
            self._outcome_table(),
            "",
            "## 可联系列表(按渠道)",
            "",
            self._contactable(),
        ]
        queue = self._review_queue()
        if queue:
            parts += [
                "",
                "## 待复核 —— 有邮箱,规模无从核实",
                "",
                "**这些不进目标表。** 平台不给粉丝数,站上也没有招商证据 ——"
                "规模是不是在带内无法判断,人是真的。",
                "",
                queue,
            ]
        if self.notes:
            parts += ["", "## 偏离与备注", ""] + [f"- {n}" for n in self.notes]
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
