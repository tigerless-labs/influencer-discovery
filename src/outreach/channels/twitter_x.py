import json
import select
import subprocess
import time
from datetime import date, timedelta
from urllib.parse import urlsplit

from ..domains import registrable_domain
from ..hop import emails_in
from ..paths import state_dir
from ..record import Audience, Candidate, Contact
from ..session import NoSession, x_session_ready
from ..topic import MAX_EVIDENCE, hits_in
from .base import Channel, register

QUERY_TIMEOUT_SECONDS = 300
IDLE_SECONDS = 90
ACCOUNTS_TIMEOUT_SECONDS = 60
PER_QUERY = 60
WINDOW_DAYS = 30
ROUNDS = 24
TIME_BUDGET_SECONDS = 2400
PLATFORM_HOSTS = {"x.com", "twitter.com", "t.co"}
ASKED_TO_WAIT = "No account available for queue"
SESSION_GONE = ("No accounts available", "no active accounts")
NESTED_TWEETS = ("quotedTweet", "retweetedTweet")


def account_db():
    """A session belongs with the state, never in the repo — the path is the guarantee."""
    return state_dir() / "accounts.db"


def twscrape_command(*args):
    return ["twscrape", "--db", str(account_db()), *args]


def _host(url):
    """A bio is hostile input: an address no parser downstream can read must not leave this module."""
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    if any(c.isspace() for c in url):
        return None
    return parsed.netloc or None


def _text(value):
    return value if isinstance(value, str) else ""


def _count(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0


@register
class TwitterX(Channel):
    name = "twitter-x"
    form = "search"
    audience_unit = "followers"
    unavailable = None
    halted = None

    def __init__(self, fetcher, config=None):
        super().__init__(fetcher, config)
        self.queries_run = 0
        self.rounds_walked = 0

    def discover(self, limit):
        if not self._ready():
            return []
        found = {}
        terms = [t for t in self.config.get("terms", []) if isinstance(t, str) and t.strip()]
        per_query = int(self.config.get("per_term", PER_QUERY))
        budget = int(self.config.get("time_budget_seconds", TIME_BUDGET_SECONDS))
        deadline = time.monotonic() + budget
        walked = self._done_queries()
        fresh = []

        try:
            for window in self.windows():
                for term in terms:
                    if len(found) >= limit or self.halted or time.monotonic() >= deadline:
                        return self._ordered(found, limit)
                    query = self.query_for(term, window)
                    if query in walked:
                        continue
                    rows = self._search(query, per_query, deadline)
                    self.queries_run += 1
                    if not self.halted:
                        fresh.append(query)
                    for user, said in self._people_in(rows):
                        self._keep(found, user, said, term)
                self.rounds_walked += 1
            return self._ordered(found, limit)
        finally:
            self._note_queries(fresh)

    def windows(self):
        """Each window is its own cursor, so depth comes from independent walks rather than one page."""
        days = max(1, int(self.config.get("window_days", WINDOW_DAYS)))
        rounds = max(1, int(self.config.get("rounds", ROUNDS)))
        today = self._today()
        for step in range(rounds):
            until = today - timedelta(days=step * days)
            yield (until - timedelta(days=days)).isoformat(), until.isoformat()

    def query_for(self, term, window):
        since, until = window
        parts = (term.strip(), _text(self.config.get("filters")).strip(), f"since:{since}", f"until:{until}")
        return " ".join(p for p in parts if p)

    def _keep(self, found, user, said, term):
        handle = _text(user.get("username"))
        if not handle or handle in found or self.already_have(handle):
            return
        evidence = hits_in(f"{_text(user.get('rawDescription'))} {_text(user.get('displayname'))} {said}")
        if not evidence:
            return
        candidate = self._to_candidate(user, term)
        candidate.signals["topic_hits"] = evidence[:MAX_EVIDENCE]
        found[handle] = candidate

    def _people_in(self, rows):
        """One response carries more than its author: quoted and retweeted authors ride along free."""
        for row in rows:
            if not isinstance(row, dict):
                continue
            for tweet in (row, *(row.get(key) for key in NESTED_TWEETS)):
                if not isinstance(tweet, dict):
                    continue
                user = tweet.get("user")
                if isinstance(user, dict) and _text(user.get("username")):
                    yield user, _text(tweet.get("rawContent"))

    def _ordered(self, found, limit):
        """The second hop is the expensive part, so whoever costs least to reach is judged first."""
        def reachability(candidate):
            cost = 0 if candidate.email else (1 if candidate.own_site else 2)
            return cost, -(candidate.audience.value if candidate.audience else 0)

        return sorted(found.values(), key=reachability)[:limit]

    def _ready(self):
        try:
            listed = subprocess.run(
                twscrape_command("accounts"), capture_output=True, text=True,
                timeout=ACCOUNTS_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.SubprocessError) as e:
            self.unavailable = f"twscrape 跑不起来:{type(e).__name__}"
            return False
        if self._has_active_account(listed.stdout):
            return True
        try:
            x_session_ready(self.config.get("session_label", "browser"))
        except NoSession as e:
            self.unavailable = str(e)
            return False
        return True

    def _has_active_account(self, listing):
        for line in (listing or "").splitlines()[1:]:
            fields = line.split()
            if len(fields) >= 3 and fields[2] in {"1", "true", "True"}:
                return True
        return False

    def _start(self, query, limit):
        return subprocess.Popen(
            twscrape_command("search", query, "--limit", str(limit)),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )

    def _search(self, query, limit, deadline=None):
        """The session is a real person's: when X asks us to wait, we leave rather than queue behind it."""
        try:
            proc = self._start(query, limit)
        except OSError as e:
            self.halted = f"twscrape 起不来:{type(e).__name__}"
            return []
        cutoff = time.monotonic() + QUERY_TIMEOUT_SECONDS
        if deadline:
            cutoff = min(cutoff, deadline)
        try:
            lines = self._read(proc, cutoff)
        finally:
            self._close(proc)
        return self._rows_in(lines)

    def _read(self, proc, cutoff):
        """A parked account says nothing at all, so silence — not a message — is the signal to leave."""
        idle = int(self.config.get("idle_seconds", IDLE_SECONDS))
        lines = []
        while True:
            remaining = cutoff - time.monotonic()
            if remaining <= 0:
                self.halted = self.halted or "取数预算用完"
                break
            if not self._readable(proc.stdout, min(idle, remaining)):
                self.halted = "X 让等下一个窗口"
                break
            line = proc.stdout.readline()
            if not line:
                break
            if line.startswith("{"):
                lines.append(line)
            elif any(marker in line for marker in SESSION_GONE):
                self.halted = "登录态没了"
                break
            elif ASKED_TO_WAIT in line:
                self.halted = "X 让等下一个窗口"
                break
        return lines

    def _readable(self, stream, timeout):
        return bool(select.select([stream], [], [], timeout)[0])

    def _rows_in(self, lines):
        rows = []
        for line in lines:
            if not line.startswith("{"):
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows

    def _close(self, proc):
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        if proc.stdout:
            proc.stdout.close()

    def _cursor(self):
        return state_dir() / "twitter-x-walked.log"

    def _done_queries(self):
        """Windows already walked stay walked: the rate limit is the scarce thing, not the disk."""
        try:
            return set(self._cursor().read_text(encoding="utf-8").splitlines())
        except OSError:
            return set()

    def _note_queries(self, queries):
        if not queries:
            return
        try:
            path = self._cursor()
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.writelines(f"{q}\n" for q in queries)
        except OSError:
            pass

    def _today(self):
        return date.today()

    def _own_site(self, user):
        for link in user.get("descriptionLinks") or []:
            if not isinstance(link, dict):
                continue
            url = link.get("url")
            if not isinstance(url, str) or not url.startswith(("http://", "https://")):
                continue
            host = _host(url)
            if not host or "." not in host or registrable_domain(url) in PLATFORM_HOSTS:
                continue
            return url
        return None

    def _to_candidate(self, user, term):
        handle = _text(user.get("username"))
        bio = _text(user.get("rawDescription"))
        candidate = Candidate(
            channel=self.name,
            person_key=handle,
            display_name=_text(user.get("displayname")) or handle,
            profile_url=f"https://x.com/{handle}",
            own_site=self._own_site(user),
            audience=Audience(_count(user.get("followersCount")), self.audience_unit, self._today().isoformat()),
            bio=bio,
            payload={
                "term": term,
                "statusesCount": _count(user.get("statusesCount")),
                "location": _text(user.get("location")),
                "verified": bool(user.get("verified") or user.get("blue")),
            },
        )
        for address in emails_in(bio):
            candidate.add_contact(Contact(address, "email", "platform_bio"))
            break
        candidate.mark_checked("profile")
        return candidate
