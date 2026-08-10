# YouTube

The largest channel on the target sheet, and one of the "two proven paths" named in the design
docs. Data access: [datalayer/public.md](../../datalayer/public.md).

## Entry point

**Search-type.** Keyword search for channels or for videos; the two yield different things:

- **Channel search** — matches channel names; easily hits hollow accounts with the keyword in the
  name.
- **Video search** — matches content, then works back from videos to the authors. **The same
  person recurring in the results is itself a signal of niche relevance**; channel search cannot
  provide that.

Prefer video search. This judgment comes from last round's runs on other platforms; unverified on
YouTube.

Starting from an existing target's channel page is also possible, but **no graph-traversal
expansion** — "related channels" has no boundary and drifts into unrelated fields; already ruled
out by the design docs.

## Getting contact info

**The channel's about page gives everything at once: the description text and the links section
are both in the initial HTML; no browser needed.**

By priority:

1. **Channel description text** — the creator's own "Business inquiries: …". Free and directly
   usable, but **fewer than one in ten channels write this**.
2. **The channel's links section** — **this channel's main source of yield**; over eighty percent
   of channels have one, averaging three or four links. But more than half point to other social
   platforms; **only those pointing to own domains are second-hop starting points**, see
   [landing-page-two-hop.md](../_shared/landing-page-two-hop.md). About seventy percent of
   channels have at least one.
3. ~~The about page's "view email address" button~~ — **this path does not exist**, rationale in
   [datalayer/public.md](../../datalayer/public.md).

So the actual shape of the YouTube chain: **take whatever the description text gives directly;
otherwise go out through the own domain; failing that, give up on the person.** The own-domain
hop hits about forty percent.

**Aggregator pages barely appear in this population** — the opposite of Instagram, where
linktr.ee is overwhelming. Don't project Instagram's shape onto this.

## Stop semantics

Search-type — stop on **consecutive no-new**; there is no natural boundary. Paging to the end is
not a stop condition here.

## Dedup key

`(channel display name, YouTube)`. The display name is machine-scraped from the channel page, not
hand-typed — that is the condition under which the dedup premise holds.

Note that `youtube.com/@handle` and `youtube.com/channel/UC…` are two addresses for the same
person; dedup doesn't look at links, so this is not a problem, but **the second hop will walk the
address entry twice**.

## Boundaries

- Description text gets truncated on list pages; the full text requires the channel page.
- Two paths sealed off at the data layer (the business-email button, the official API's email
  field): see [datalayer/public.md](../../datalayer/public.md).
  **The only yield here is the description text and the links section.**
- The links section mixes in payment/tip-jar, course-community, and scheduling links hosted by
  third parties. **They are not own domains**; used as second-hop starting points they fetch a
  platform, not a person.

## To verify

- How big the video-search vs channel-search quality gap is on YouTube (the judgment comes from
  runs on other platforms). The video-search path works via CLI, and the same-person recurrence
  phenomenon does appear, but the two paths haven't been compared head-to-head.
- Stability of channel display names — the dedup premise depends on it.
