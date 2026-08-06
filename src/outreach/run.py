import argparse
import json
import tomllib
from datetime import date

from . import channels as channel_registry
from .fetch import Fetcher
from .gate import Gate
from .paths import repo_config_dir
from .record import Outcome
from .report import Report
from .store import Store
from .walk import SecondHop

DEFAULT_BAND = (5000, 100000)


def load_config(name):
    path = repo_config_dir() / name
    return tomllib.loads(path.read_text(encoding="utf-8"))


class Run:
    def __init__(self, run_id, per_channel, band, priority, store=None):
        self.run_id = run_id
        self.per_channel = per_channel
        self.gate = Gate(band)
        self.store = store or Store()
        self.fetcher = Fetcher(run_id, store=self.store)
        self.hop = SecondHop(self.fetcher, self.store, run_id)
        self.report = Report(run_id, {"per_channel": per_channel, "band": band, "priority": priority})

    def channel(self, name, config):
        adapter = channel_registry.build(name, self.fetcher, config)
        raw = adapter.discover(self.per_channel * 4)
        fresh = [c for c in raw if not self.store.is_seen(c.dedup_key)]

        judged = []
        for candidate in fresh:
            if len(judged) >= self.per_channel:
                break
            needs_signal = candidate.audience is None or candidate.audience.unit != "followers"
            if candidate.own_site and (not candidate.email or needs_signal):
                self.hop.walk(candidate)
            verdict = self.gate.judge(candidate)
            candidate.outcome = verdict.outcome
            candidate.signals["verdict_reason"] = verdict.reason
            candidate.signals["band_applied"] = verdict.band_applied
            self.store.record(candidate, run_id=self.run_id)
            judged.append(candidate)

        stop = "凑够" if len(judged) >= self.per_channel else (
            "翻到底" if adapter.form == "directory" else "连续无新"
        )
        self.report.add(name, judged, stop, self.per_channel)
        return judged

    def qualified(self):
        return [
            c
            for block in self.report.channels.values()
            for c in block["qualified"]
        ]


def summarise(run_id, per_channel, band, priority, store=None):
    """The contactable list is a view over the store, not a fourth place to keep it."""
    store = store or Store()
    report = Report(run_id, {"per_channel": per_channel, "band": band, "priority": priority})
    by_channel = {}
    for candidate in store.people():
        if candidate.outcome is None:
            continue
        by_channel.setdefault(candidate.channel, []).append(candidate)
    for channel, candidates in sorted(by_channel.items()):
        report.add(channel, candidates, "见各轮报告", per_channel)
    return report


def append_to_sheet(store=None):
    from .paths import credential, state_dir
    from .record import Outcome
    from .sheet import SheetsApi, SheetsUnavailable, TargetSheet, access_token

    store = store or Store()
    config = load_config("sheet.toml")
    rows = [c for c in store.people() if c.outcome is Outcome.QUALIFIED]

    staged = state_dir() / "pending-sheet-rows.jsonl"
    staged.write_text(
        "\n".join(json.dumps(c.to_row(), ensure_ascii=False) for c in rows), encoding="utf-8"
    )

    spreadsheet_id = credential("OUTREACH_SPREADSHEET_ID")
    if not spreadsheet_id:
        return staged, "OUTREACH_SPREADSHEET_ID 未设置"
    try:
        api = SheetsApi(spreadsheet_id, access_token())
        TargetSheet(api, config["tab"], config["columns"]).append(rows)
    except SheetsUnavailable as e:
        return staged, f"取不到 token:{e}"
    except Exception as e:
        return staged, f"{type(e).__name__}: {e}"
    return staged, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channels", default="")
    parser.add_argument("--per-channel", type=int, default=10)
    parser.add_argument("--run-id", default=date.today().isoformat())
    parser.add_argument("--summarise", action="store_true")
    parser.add_argument("--append-sheet", action="store_true")
    args = parser.parse_args()

    if args.append_sheet:
        staged, problem = append_to_sheet()
        print(f"staged: {staged}")
        print(f"blocked: {problem}" if problem else "appended")
        return

    if args.summarise:
        report = summarise(args.run_id, args.per_channel, DEFAULT_BAND, "接单意愿优先于规模")
        print(report.save())
        return

    config = load_config("channels.toml")
    names = [n for n in (args.channels.split(",") if args.channels else config) if n in config]

    run = Run(args.run_id, args.per_channel, DEFAULT_BAND, "接单意愿优先于规模")
    for name in names:
        try:
            run.channel(name, config[name])
        except Exception as e:  # a channel that dies must not take the run with it
            run.report.note(f"`{name}` 中断:{type(e).__name__} {e}")
    print(run.report.save())


if __name__ == "__main__":
    main()
