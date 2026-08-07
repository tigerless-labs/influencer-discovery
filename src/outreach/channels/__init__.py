from . import (  # noqa: F401
    devto,
    freecodecamp,
    hashnode,
    instagram,
    mastodon,
    microblog,
    newsletter,
    podcast,
    reddit,
    selfhosted,
    threads,
    twitter_x,
    tiktok,
    wordpress,
    youtube,
)
from .base import REGISTRY


def build(name, fetcher, config):
    return REGISTRY[name](fetcher, config)


def known():
    return sorted(REGISTRY)
