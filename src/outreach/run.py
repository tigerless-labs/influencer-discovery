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
from .export import write_xlsx
from .walk import SecondHop

DEFAULT_BAND = (5000, 200000)
DEFAULT_SUBJECT = "ai"
DEFAULT_POOL_FACTOR = 25


def load_config(name):
    path = repo_config_dir() / name
    return tomllib.loads(path.read_text(encoding="utf-8"))


def tier_of(entry):
    """The methodology directory owns tier membership; this only reads it back."""
    return int(entry["methodology"].split("/")[0].split("-")[0])


def select(config, names="", tiers=""):
    wanted = [n.strip() for n in names.split(",") if n.strip()]
    wanted_tiers = {int(t) for t in tiers.split(",") if t.strip()}
    picked = []
    for name, entry in config.items():
        if not isinstance(entry, dict):
            continue
        if wanted and name not in wanted:
            continue
        if wanted_tiers and tier_of(entry) not in wanted_tiers:
            continue
        picked.append(name)
    return picked


class Run:
    def __init__(self, run_id, per_channel, band, priority, store=None,
                 pool_factor=DEFAULT_POOL_FACTOR, total=None, subject=DEFAULT_SUBJECT):
        self.run_id = run_id
        self.per_channel = per_channel
        self.pool_factor = pool_factor
        self.gate = Gate(band, subject)
        self.store = store or Store()
        self.fetcher = Fetcher(run_id, store=self.store)
        self.hop = SecondHop(self.fetcher, self.store, run_id)
        self.total = total
        self.subject = subject
        self.qualified_so_far = 0
        self.report = Report(run_id, {"per_channel": per_channel, "band": band, "priority": priority,
                                      "total": total or per_channel, "subject": subject})

    def channel(self, name, config):
        adapter = channel_registry.build(name, self.fetcher, config)
        adapter.already_have = lambda person_key: self.store.is_seen((person_key, name))
        raw = adapter.discover(self.per_channel * self.pool_factor)
        fresh = [c for c in raw if not self.store.is_seen(c.dedup_key)]

        judged = []
        qualified = 0
        for candidate in fresh:
            if qualified >= self.per_channel or (
                self.total and self.qualified_so_far >= self.total
            ):
                self._park(candidate)
                continue
            needs_signal = candidate.audience is None or candidate.audience.unit != "followers"
            if candidate.own_site and (not candidate.email or needs_signal):
                self.hop.walk(candidate)
            verdict = self.gate.judge(candidate)
            candidate.outcome = verdict.outcome
            candidate.signals["verdict_reason"] = verdict.reason
            candidate.signals["band_applied"] = verdict.band_applied
            self.store.record(candidate, run_id=self.run_id)
            judged.append(candidate)
            if verdict.writes_to_sheet:
                qualified += 1
                self.qualified_so_far += 1

        if getattr(adapter, "unavailable", None):
            self.report.note(f"`{name}` 跳过:{adapter.unavailable}")
        met = qualified >= self.per_channel
        stop = "凑够" if met else ("翻到底" if adapter.form == "directory" else "连续无新")
        shortfall = None if met else (
            "候选不足" if len(fresh) < self.per_channel else "闸门卡住"
        )
        judged = self.gate.rank(judged)
        self.report.add(name, judged, stop, self.per_channel, shortfall=shortfall)
        return judged

    def _park(self, candidate):
        """Discovery already paid for this person, so the log owes them a row even unjudged."""
        candidate.signals["pending_judgement"] = True
        self.store.record(candidate, run_id=self.run_id)

    def qualified(self):
        return [
            c
            for block in self.report.channels.values()
            for c in block["qualified"]
        ]


def summarise(run_id, per_channel, band, priority, store=None, total=None, subject=DEFAULT_SUBJECT):
    """The contactable list is a view over the store, not a fourth place to keep it."""
    store = store or Store()
    report = Report(run_id, {"per_channel": per_channel, "band": band, "priority": priority,
                             "total": total or per_channel, "subject": subject})
    by_channel = {}
    for candidate in store.people():
        if candidate.outcome is None:
            continue
        by_channel.setdefault(candidate.channel, []).append(candidate)
    ranker = Gate(band, subject)
    for channel, candidates in sorted(by_channel.items()):
        report.add(channel, ranker.rank(candidates), "见各轮报告", per_channel)
    return report


DERIVED_SIGNALS = ("is_buyer", "buyer_reason", "sponsor_page", "own_site_is_a_platform")


def _judgement(candidate):
    """Stale evidence behind a still-correct verdict is a wrong record, so the evidence is compared too."""
    return (
        candidate.outcome,
        sorted(c.value for c in candidate.contacts),
        tuple(candidate.signals.get("topic_hits") or ()),
        candidate.signals.get("verdict_reason"),
        candidate.signals.get("in_band"),
    )


def rejudge(run_id, band, store=None, replay=False):
    """The log is a cache, not the authority: a corrected judgement supersedes the stored one."""
    from .fetch import ReplayFetcher
    from .hop import is_an_inbox

    store = store or Store()
    gate = Gate(band)
    hop = SecondHop(ReplayFetcher(), store, run_id) if replay else None
    corrected = []
    for candidate in store.people():
        if candidate.outcome is None:
            continue
        before = _judgement(candidate)
        candidate.contacts = [c for c in candidate.contacts if is_an_inbox(c.value)]
        if hop and candidate.own_site:
            for signal in DERIVED_SIGNALS:
                candidate.signals.pop(signal, None)
            hop.walk(candidate)
            candidate.contacts = [c for c in candidate.contacts if is_an_inbox(c.value)]
        verdict = gate.judge(candidate)
        candidate.outcome = verdict.outcome
        candidate.signals["verdict_reason"] = verdict.reason
        candidate.signals["band_applied"] = verdict.band_applied
        if before != _judgement(candidate):
            store.record(candidate, run_id=run_id)
            corrected.append(candidate)
    return corrected


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
    parser.add_argument("--tiers", default="")
    parser.add_argument("--per-channel", type=int, default=10)
    parser.add_argument("--total", type=int, default=None)
    parser.add_argument("--subject", default=DEFAULT_SUBJECT)
    parser.add_argument("--run-id", default=date.today().isoformat())
    parser.add_argument("--summarise", action="store_true")
    parser.add_argument("--rejudge", action="store_true")
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--append-sheet", action="store_true")
    parser.add_argument("--export-xlsx", default="")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    if args.compact:
        from .fetch import RawStore

        store = Store()
        before, after = store.compact_sites()
        print(f"sites.jsonl  {before} -> {after} 行")
        raw = RawStore()
        print(f"raw          折叠 {raw.migrate()} 个按轮存的文件")
        print(f"raw          压缩 {raw.pack()} 个 blob")
        return

    if args.export_xlsx:
        print(write_xlsx(Store(), DEFAULT_BAND, name=args.export_xlsx))
        return

    if args.rejudge:
        for candidate in rejudge(args.run_id, DEFAULT_BAND, replay=args.replay):
            print(f"{candidate.channel}/{candidate.person_key} -> {candidate.outcome.value}")
        return

    if args.append_sheet:
        staged, problem = append_to_sheet()
        print(f"staged: {staged}")
        print(f"blocked: {problem}" if problem else "appended")
        return

    if args.summarise:
        report = summarise(args.run_id, args.per_channel, DEFAULT_BAND, "规模只排序,不筛人",
                           total=args.total, subject=args.subject)
        print(report.save())
        return

    config = load_config("channels.toml")
    names = select(config, names=args.channels, tiers=args.tiers)

    run = Run(
        args.run_id,
        args.per_channel,
        DEFAULT_BAND,
        "规模只排序,不筛人",
        pool_factor=config.get("pool_factor", DEFAULT_POOL_FACTOR),
        total=args.total,
        subject=args.subject,
    )
    for name in names:
        try:
            run.channel(name, config[name])
        except Exception as e:  # a channel that dies must not take the run with it
            run.report.note(f"`{name}` 中断:{type(e).__name__} {e}")
    print(run.report.save())
    print(write_xlsx(run.store, DEFAULT_BAND))


if __name__ == "__main__":
    main()
