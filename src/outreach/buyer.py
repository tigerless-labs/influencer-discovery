import re

from .page import visible_text

PRODUCT = [
    re.compile(p, re.I)
    for p in (
        r"\bpricing\b", r"start (your )?free trial", r"\bsign ?up free\b", r"get started free",
        r"download on the app store", r"\bget it on google play\b", r"\brequest a demo\b",
        r"\bbook a demo\b", r"\bper month\b.{0,40}\bper user\b", r"\bstart building\b",
    )
]
AUDIENCE = [
    re.compile(p, re.I)
    for p in (
        r"\bsubscribe\b", r"\bnewsletter\b", r"\barchive\b", r"\brss\b", r"\bepisodes?\b",
        r"\bblog\b", r"\bwriting\b", r"\bessays?\b", r"\bposts?\b", r"\bpodcast\b",
    )
]


def looks_like_a_product_site(html):
    """Conservative on purpose: a wrong buyer call silently drops a real target."""
    text = visible_text(html)
    product_hits = sum(bool(p.search(text)) for p in PRODUCT)
    audience_hits = sum(bool(p.search(text)) for p in AUDIENCE)
    return product_hits >= 2 and audience_hits == 0
