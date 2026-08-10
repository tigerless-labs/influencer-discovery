import gzip
import hashlib
import json
import pathlib
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from .domains import registrable_domain
from .paths import state_dir

USER_AGENT = "influencer-discovery/0.1 (+https://tigerless.com; polite crawler)"
HOST_GAP_SECONDS = 1.5
STOP_CODES = {403, 429}
ALLOWED_SCHEMES = {"http", "https"}


class Blocked(Exception):
    pass


class RawStore:
    """Content-addressed: one address, one blob, however many runs touch it.
    Each run keeps a manifest of what it saw, so a run is still replayable on its own."""

    def __init__(self, root=None):
        self.root = pathlib.Path(root) if root else state_dir() / "raw"
        self.blob_dir = self.root / "blobs"

    @staticmethod
    def digest_of(url):
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def blobs(self):
        return sorted(self.blob_dir.glob("*.json*"))

    def _blob_path(self, digest):
        packed = self.blob_dir / f"{digest}.json.gz"
        return packed if packed.exists() else self.blob_dir / f"{digest}.json"

    @staticmethod
    def _read_blob(path):
        opener = gzip.open if path.suffix == ".gz" else open
        try:
            with opener(path, "rt", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError, EOFError):
            return None

    def _manifest(self, run_id):
        return self.root / f"{run_id}.manifest"

    def digests_for(self, run_id):
        path = self._manifest(run_id)
        return set(path.read_text(encoding="utf-8").split()) if path.exists() else set()

    def note(self, run_id, digest):
        if not run_id or digest in self.digests_for(run_id):
            return
        path = self._manifest(run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(digest + "\n")

    def put(self, url, body, run_id=None):
        digest = self.digest_of(url)
        blob = self._blob_path(digest)
        if not blob.exists():
            self.blob_dir.mkdir(parents=True, exist_ok=True)
            blob = self.blob_dir / f"{digest}.json.gz"
            with gzip.open(blob, "wt", encoding="utf-8", compresslevel=6) as f:
                json.dump({"url": url, "body": body}, f, ensure_ascii=False)
        self.note(run_id, digest)
        return blob

    def get(self, url, run_ids=None):
        digest = self.digest_of(url)
        if run_ids is not None and not any(digest in self.digests_for(r) for r in run_ids):
            return None
        blob = self._blob_path(digest)
        if not blob.exists():
            return None
        record = self._read_blob(blob)
        return record.get("body") if record else None

    def pack(self):
        """Compresses blobs left in plain form. Lossless, so it needs no policy decision."""
        packed = 0
        for blob in sorted(self.blob_dir.glob("*.json")):
            record = self._read_blob(blob)
            if record is None:
                blob.unlink(missing_ok=True)
                continue
            with gzip.open(blob.with_suffix(".json.gz"), "wt", encoding="utf-8", compresslevel=6) as f:
                json.dump(record, f, ensure_ascii=False)
            blob.unlink()
            packed += 1
        return packed

    def migrate(self):
        """Folds the old raw/<run>/<digest>.json layout in. First body wins; nothing is rewritten."""
        moved = 0
        for directory in sorted(p for p in self.root.glob("*") if p.is_dir()):
            if directory == self.blob_dir:
                continue
            for old in sorted(directory.glob("*.json")):
                try:
                    record = json.loads(old.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    old.unlink(missing_ok=True)
                    continue
                self.put(record.get("url", ""), record.get("body", ""), run_id=directory.name)
                old.unlink(missing_ok=True)
                moved += 1
            if not any(directory.iterdir()):
                directory.rmdir()
        return moved



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
        self.reused = 0
        self.raw = RawStore()

    def _wait(self, host):
        with self._lock:
            elapsed = time.monotonic() - self._last.get(host, 0)
            if elapsed < self.gap:
                time.sleep(self.gap - elapsed)
            self._last[host] = time.monotonic()

    def _persist(self, url, body):
        self.raw.put(url, body, run_id=self.run_id)

    def get(self, url, headers=None, persist=True, reuse=False):
        if reuse:
            kept = self.raw.get(url)
            if kept is not None:
                self.raw.note(self.run_id, self.raw.digest_of(url))
                self.reused += 1
                return kept
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

    def try_get(self, url, headers=None, reuse=False, persist=True):
        try:
            return self.get(url, headers, persist=persist, reuse=reuse)
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

    def __init__(self, run_ids=None, raw=None):
        self.raw = raw or RawStore()
        self.run_ids = run_ids

    def try_get(self, url, headers=None, reuse=False, persist=True):
        return self.raw.get(url, run_ids=self.run_ids)

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
