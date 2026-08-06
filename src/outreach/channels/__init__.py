from . import (  # noqa: F401
    devto,
    instagram,
    mastodon,
    microblog,
    newsletter,
    podcast,
    reddit,
    selfhosted,
    tiktok,
    wordpress,
)
from .base import REGISTRY


def build(name, fetcher, config):
    return REGISTRY[name](fetcher, config)


def known():
    return sorted(REGISTRY)
