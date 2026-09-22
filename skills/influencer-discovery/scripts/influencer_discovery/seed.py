import csv
import re

from .sheet import HeaderMismatch

HANDLE_IN_LINK = re.compile(r"^https?://(?:www\.|m\.)?youtube\.com/@([\w.\-]+)", re.I)


def _youtube_handle(link):
    match = HANDLE_IN_LINK.match((link or "").strip())
    return match.group(1).lower() if match else None


KEY_FROM_LINK = {"youtube": _youtube_handle}


def _column(headers, title):
    try:
        return headers.index(title)
    except ValueError:
        raise HeaderMismatch(f"missing column {title!r}") from None


def keys_from_rows(headers, rows, mapping, channel):
    key_of = KEY_FROM_LINK.get(channel)
    if key_of is None:
        raise ValueError(f"no seed rule for {channel!r}")
    platform_at = _column(headers, mapping["channel"])
    link_at = _column(headers, mapping["profile_url"])
    keys = []
    for row in rows:
        row = list(row) + [""] * (len(headers) - len(row))
        if row[platform_at].strip().lower() != channel:
            continue
        key = key_of(row[link_at])
        if key and (key, channel) not in keys:
            keys.append((key, channel))
    return keys


def seed_channel(store, headers, rows, mapping, channel):
    keys = keys_from_rows(headers, rows, mapping, channel)
    before = len(store.raw_lines(channel))
    store.seed(keys, run_id="seed")
    return len(store.raw_lines(channel)) - before


def read_export(path):
    with open(path, newline="", encoding="utf-8") as f:
        table = list(csv.reader(f))
    return (table[0], table[1:]) if table else ([], [])
