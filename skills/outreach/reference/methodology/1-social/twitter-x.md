# X / Twitter

**Run it.** Capability boundary: [datalayer/twitter-x.md](../../datalayer/twitter-x.md) —
anonymous access only gives display name and bio; **both discovery and external links require a
logged-in session**.

The fundamental difference from [linkedin.md](../_not-run/linkedin.md) is exactly here:
**this platform has discovery** — search can find people from topics. Over there, even fully
unlocked, that step doesn't exist.

## No email field here

What's obtainable is bio text and one external link. Contact info is either written into the bio
by the creator or sits at the link's landing — **this platform is another starting point for the
second hop**, see [landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

## Entry point

**Search-type.** Search content by topic and converge on the authors; don't search users — same
as everywhere else, user search matches names and mostly returns hollow accounts;
**the same person recurring in content results is itself a signal of niche relevance**.

## Getting contact info

```
① topic search → authors (with bio, external link, follower count)
② extract email from bio
③ if nothing, follow the external link into the second hop
```

**The bio link is a single slot, not a links section** — unlike YouTube's three or four at a
time, there is only one position here, so whether that one link is an own domain matters all the
more. **Pass the exclusion list first** (aggregator pages, tip-jar pages, course communities),
list in [landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

**Follower count is public**; client-side filtering costs no extra request — same as Mastodon and
YouTube, and better than the Blog / Newsletter / Podcast tiers.

## Throttle by risk, not by politeness

Data access reuses **the user's own real account**; the consequences of being flagged as
automation land on that account.

**Serial, low-frequency, no deep pagination.** This overrides any yield consideration.

## Stop semantics

Search-type — **consecutive no-new**.

## Dedup key

`(handle, X)`. Handles are unique and stable; the dedup premise is solid.

## Boundaries

- No posting, no replying, no liking, no following, no DMs.
- The anonymous path only suffices for identity backfill; **it cannot supply the second-hop
  starting point** — no external links.
- Short links need one expansion to learn the landing; the expansion counts as a hop.

## To verify

**This tier's method is written in the shape of other channels; not a single number has been
measured.** Run one round before relying on it:

- Share of bios stating an email. Anecdotally higher in technical niches than lifestyle ones;
  unmeasured on this project's population.
- Share of external links that are own domains (versus YouTube's seventy percent).
- Overlap between topic-searched people and the existing channels.
- What frequency avoids triggering automation detection — **figure this out first**; it decides
  whether this tier can run routinely.

## Before running

**Prefer browser cookies; there is no second option** — the anonymous API path has long been
closed; discovery and external links are both behind login.

**When the account pool is empty, refill once from the browser**; no manual account adding
needed. If the browser isn't logged into x.com, skip this channel for the whole round and state
in the report what is missing — without blocking the other channels.

Data-access boundary: [datalayer/twitter-x.md](../../datalayer/twitter-x.md).
