# Instagram

Data access: [datalayer/instagram.md](../../datalayer/instagram.md); whether to take this path:
[cost-ranking.md](../_shared/cost-ranking.md).

Search results carry bio, external link, **and follower count** (re-verified 2026-08-07). So the
scale threshold is usable at the discovery stage; people below it never even need a site crawl —
the profile endpoint is only a fallback for when search omits the follower count.

## Full chain

```
① bio keyword search          1 credit/call    → a batch of bloggers with bio + external link + follower count
② multiple query variants     0 credit         → heavy overlap between variants; dedup by username
③ follower count (fallback)   1 credit/person  → only called when ① omits it
④ extract email from bio      0 credit
⑤ no email → second hop       0 credit
```

### ① bio keyword search

```
GET /v1/instagram/search/profiles?query=<bio keywords>
```

**`query` matches bio text, not usernames.** Write the filter conditions into the query itself;
people filtered out never cost a call:

```
"business inquiries" <niche term>     only people who deliberately list business contact
"@gmail.com" <niche term>             locks onto bios containing an email
"linktr.ee" <niche term>              locks onto people with a landing page
<niche term> <city name>              de facto region filter
```

**Multi-word queries can 500.** `ai agent` works; `ai tools` errors consistently — change the
term, don't retry.

From `profiles` take:

```
username · full_name · biography · bio_links[].url · external_url
category_name · is_business_account · is_professional_account · is_verified · is_private
```

### ② multiple query variants

Underneath it wraps the Google index (the cursor is a Google results page); **a single query
yields roughly a few dozen to a hundred-odd results**. Volume comes from variants, not
pagination. **Dedup must happen during accumulation**, otherwise the same person is fetched
multiple times.

Sporadic 500s: skip that query and continue; don't retry.

### ③ client-side filter

Drop anyone under 1,000 followers; it is all noise.

### ④⑤ email extraction and second hop

Regex over `biography`. If nothing, follow `bio_links[].url` or `external_url` into
[landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

## Expected hits

```
email in bio                 ~22%
has external link            ~88%
recovered via landing page   ~36% (of those with no email but a link)
reachable (email ∪ link)     ~94%
```

`linktr.ee` is the overwhelming top external link, followed by `youtube.com`, `stan.store`,
`bit.ly`. **Creators don't put emails in bios; they hang a Linktree** — all the marginal yield is
in the second hop, and the second hop costs no credits.

Landing-page finds contain noise (template placeholders, site-builder shared emails); after
denoising, total net hit rate is about 38–40%. Noise types:
[landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

**For those where both email and link come up empty**, take the same handle to Threads for
another bio, see [threads.md](threads.md).

## Parsing pitfalls

- **The email regex must run on the raw `biography` string, not on the string after
  `json.dumps`.** dumps turns newlines into a literal `\n`; `\w` matches that `n`, extracting
  glued addresses like `nJoey@example.com`.
- **Strip trailing punctuation.** `xxx@gmail.com。` gets extracted with the full stop attached.

## Skipped

- **`/v1/instagram/profile` is fallback only.** Contact info, topic judgment, and follower count
  are already in the search results, and the extra hop doesn't buy `business_email` either
  (always null, see the data layer). Out of nine hundred people in one round, it fell back only
  four times.
- **No `edge_related_profiles` snowballing.** One seed expands to 32; a single layer eats a large
  share of the quota, while bio keyword search hits the niche directly — cheaper and more precise.
