import hashlib
import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from .domains import registrable_domain
from .paths import state_dir

USER_AGENT = "outreach-research/0.1 (+https://tigerless.com; polite crawler)"
HOST_GAP_SECONDS = 1.5
STOP_CODES = {403, 429}
ALLOWED_SCHEMES = {"http", "https"}


class Blocked(Exception):
    pass


class Fetcher:
    """The one place requests leave from. It can read; it cannot write."""

    def __init__(self, run_id, store=None, gap=HOST_GAP_SECONDS, timeout=25):
        self.run_id = run_id
        self.store = store
        self.gap = gap
        self.timeout = timeout
        self._last = {}
        self._lock = threading.Lock()
        self._blocked = set()
        self.raw_dir = state_dir() / "raw" / run_id

    def _wait(self, host):
        with self._lock:
            elapsed = time.monotonic() - self._last.get(host, 0)
            if elapsed < self.gap:
                time.sleep(self.gap - elapsed)
            self._last[host] = time.monotonic()

    def _persist(self, url, body):
        digest = hashlib.sha256(url.encode()).hexdigest()[:16]
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        (self.raw_dir / f"{digest}.json").write_text(
            json.dumps({"url": url, "body": body}, ensure_ascii=False), encoding="utf-8"
        )

    def get(self, url, headers=None, persist=True):
        parsed = urllib.parse.urlparse(url or "")
        if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
            self._fail(url, "not an http address")
            raise Blocked(f"{url} -> not an http address")
        host = parsed.netloc
        if host in self._blocked:
            raise Blocked(f"{host} already refused this run")
        self._wait(host)
        request = urllib.request.Request(url)
        request.add_header("User-Agent", USER_AGENT)
        request.add_header("Accept", "*/*")
        for key, value in (headers or {}).items():
            request.add_header(key, value)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in STOP_CODES:
                self._blocked.add(host)
            self._fail(url, f"http {e.code}")
            raise Blocked(f"{url} -> {e.code}") from None
        except Exception as e:
            self._fail(url, type(e).__name__)
            raise Blocked(f"{url} -> {type(e).__name__}") from None
        if persist:
            self._persist(url, body)
        return body

    def get_json(self, url, headers=None):
        try:
            return json.loads(self.get(url, headers))
        except json.JSONDecodeError:
            self._fail(url, "not json")
            raise Blocked(f"{url} -> not json") from None

    def try_get(self, url, headers=None):
        try:
            return self.get(url, headers)
        except Blocked:
            return None

    def try_json(self, url, headers=None):
        try:
            return self.get_json(url, headers)
        except Blocked:
            return None

    def _fail(self, url, reason):
        if self.store:
            self.store.record_failure(url, reason, run_id=self.run_id)

    def site_blocked(self, url):
        return urllib.parse.urlparse(url).netloc in self._blocked


class ReplayFetcher:
    """Serves what earlier runs already paid for. It cannot reach the network at all."""

    def __init__(self, run_ids=None):
        root = state_dir() / "raw"
        self.dirs = (
            [root / r for r in run_ids] if run_ids else sorted(p for p in root.glob("*") if p.is_dir())
        )

    def try_get(self, url, headers=None):
        digest = hashlib.sha256(url.encode()).hexdigest()[:16]
        for directory in self.dirs:
            path = directory / f"{digest}.json"
            if path.exists():
                try:
                    return json.loads(path.read_text(encoding="utf-8")).get("body")
                except json.JSONDecodeError:
                    continue
        return None

    def try_json(self, url, headers=None):
        body = self.try_get(url)
        try:
            return json.loads(body) if body else None
        except json.JSONDecodeError:
            return None

    def site_blocked(self, url):
        return False


def pmap(fn, items, workers=6):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, items))


def same_site(a, b):
    return registrable_domain(a) == registrable_domain(b)
