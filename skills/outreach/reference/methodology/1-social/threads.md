# Threads

Data access: [datalayer/threads.md](../../datalayer/threads.md); whether to take this path:
[cost-ranking.md](../_shared/cost-ranking.md).

The search endpoint returns neither follower count nor bio — two steps are mandatory: get handles
first, then fetch profile pages one by one.

## Full chain

```
① content search           1 credit         → ~20 posts, deduped to a dozen-plus authors (no follower count, no bio)
② per-person profile       1 credit/person  → follower_count + biography + bio_links + niche tag
③ client-side filter       0 credit         → follower range, niche tag
④ extract email from bio   0 credit
⑤ no email → second hop    0 credit
```

**Filtering happens after ②.** Follower count, bio, and niche tags all live only on the profile
page, so before ② the only usable things are `username`, `full_name`, `is_verified`, and the post
body from the search results.
**Rough-filter on body relevance first, then decide whose profile to fetch.**

### ① content search

Search posts by keyword; take `user.username` from each post. **The same author recurring is a
signal of niche relevance**; dedup by username and count occurrences.

Don't use user search: it matches usernames rather than content, has fewer fields, and equally
omits follower count.

**Scale via date windows, not new terms.** The same keyword paged backward one week per window;
each window is a fresh batch of authors. **Give every term one layer first, then deepen across
the board** — wherever the budget cuts off, you won't have covered only the first few terms.

### ①.5 deciding whose profile to pay for

Profiles are billed per person, so the ranking happens between ① and ②, based only on what the
search results carry: **occurrence count → post `like_count` → topical hit in the post body**.
Private accounts: don't pay.

### ② per-person profile

One call returns follower count, full bio, external links, and the platform's own niche tag.
**The niche tag is unique to this platform** — nowhere else has it, and it can be used directly
as a filter condition.

### ③ client-side filter

Filter by follower count and niche tag. **Accounts surfaced by keyword search are mostly tiny**;
the median is a few hundred followers — this step drops most people.

### ④⑤ email extraction and second hop

Regex over `biography`. If nothing, follow `bio_links[].url` into
[landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

**Take the `url` field for external links, not the platform-wrapped redirect version.**

**There are often multiple external links; walk only one: own domain first, then aggregator page;
platform pages don't count as own sites.** Taking the first by array order picks the one pointing
back to a social platform, and that hop is guaranteed to come back empty-handed.

## Expected hits

```
follower count, bio present   100%
email in bio                  near 0     ← vastly below TikTok's 53%
has external link             ~50%
reachable                     ~50%
```

**This channel gets almost no emails directly from bios; all the yield is in the second hop.**
External-link landings include personal domains as well as community and video platforms — the
latter are not own sites and must pass the exclusion list first, list in
[landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

The sample is only ten people; **the ratios are still rough**, but "no emails in bios" and "small
accounts overwhelmingly dominate" are both clear enough.

## A free path when the handle is already known

**Burns no credits but gets no external links** — so it cannot replace the chain above; only two
use cases: **backfilling follower count and bio for people already on the sheet**, and **trying
another bio when Instagram's email and link both came up empty**.

Two steps, tried in order:

**① Federation first.** Query any Mastodon instance for the account as `<handle>@threads.net`,
getting **structured JSON**: follower count, bio. No credentials needed.
**"Not found" is the norm** — it means the person hasn't enabled fediverse sharing, not an error;
fall to step two.

**② If empty, fetch the profile page.** Plain HTTP; everything needed is in the Open Graph tags.
**Follower count and bio are concatenated into one description string** — split it yourself;
decode HTML entities before splitting, general rule in
[landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

## Overlap with Instagram

**Handles are shared with Instagram**; the two searches surface a large fraction of the same
people. The dedup key is `(person, platform)`, so one person lands as two rows — accepted by
design.

**Run order: Instagram first, then Threads; before ②, check the log and skip handles already
seen.**

## Stop semantics

Search-type — **consecutive no-new**.

## Dedup key

`(handle, Threads)`. Handles are unique and stable.

## Boundaries

- No posting, no replying, no following.
- **The free path gets no external links**, and external links are this tier's main yield.
- A window is about twenty posts; a keyword's depth is however many windows you can page back.

## To verify

- **Sample size.** Ten-person ratios are too rough; "email in bio near zero" in particular needs
  confirming at a hundred-plus people.
- How accurate `like_count` is as a scale proxy — on a sample of a dozen-plus it only shows as a
  weak signal.
- The actual overlap ratio with Instagram.
- The niche tag's value range; it may be better suited than follower count as the first filter.
