# Mastodon

**The only channel where "own domain" requires no inference** — the platform does attribution
verification itself. Capability boundary: [datalayer/mastodon.md](../../datalayer/mastodon.md).

Elsewhere, own-domain attribution relies on statistics (Reddit's "posted by only one person") or
on exclusion lists (YouTube's tip-jar pages); here it relies on `rel="me"` mutual confirmation:
**the platform only stamps verification when the site links back to the account**.
The stamped link is their site, zero ambiguity.

## Entry points

Neither needs a seed; use them crosswise:

- **Account directory** — paginated by activity, one page of accounts at a time, **carrying bio,
  links, and follower count directly**; no per-profile lookups needed.
- **Topic timeline** — fetch posts by hashtag and converge on the authors. This path filters for
  the niche; the directory path doesn't.

**Run across multiple instances.** Federation has no global view; a single instance only sees the
part of the network it knows.

## Getting contact info

```
① directory or hashtag → accounts (with bio + fields + follower count)
② take the verified-stamp link in fields = their own domain
③ second hop to dig out the email
```

**Emails written directly in bios are rare**; don't count on that step — this channel's value is
the quality of its second-hop starting points, not direct hits. Landing handling:
[landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

**Do not treat unverified links as own domains**; fall back to the general exclusion list and
judge from there.

**The volume is on the fallback path.** Verified-stamp accounts are a minority; links that pass
the exclusion list are the majority — accepting only verified stamps throws away three quarters
of the walkable sites. Accept both, and record verification status on the candidate.

**Emails hung directly in `fields` are as common as emails in bios**; scan both.

**`@username@instance.domain` in a bio is not an email.** It looks like an address; it is a
fediverse handle and must be excluded during email extraction.

## Follower count is free

`followers_count` is already in the directory response; **client-side filtering costs no extra
request**. That is its advantage over Blog / Newsletter / Podcast — none of those three tiers
have a public audience size.

**So spend the scale threshold at the discovery stage**; don't defer it past the second hop.
Paging is free, walking sites costs time; sort by follower count first, then decide whom to walk,
and spend the limited site visits on the biggest audiences.

## Stop semantics

The directory path is **directory-type**: done when paged to the end. The hashtag path is
**search-type**: stop on consecutive no-new.
**Track the two separately**, otherwise you can't see which path is still worth the spend.

## Dedup key

`(username@instance.domain, Mastodon)`.

**The instance domain is mandatory.** Username alone collides across instances; same name,
different person is the norm. When one person has accounts on multiple instances, converge on the
verified domain in their fields.

## Boundaries

- **Accounts can opt out of discovery**; the directory is not exhaustive — paging to the end does
  not mean seeing everyone.
- Bios are HTML fragments; decode before email extraction, rationale in
  [landing-page-two-hop.md](../_shared/landing-page-two-hop.md).
- No following, no boosting, no DMs.

## Scale means not paging deep enough, not an empty platform

The earlier conclusion "four instances paged to the end, only three people over five thousand" is
void — it came from paging too shallow. After expanding to twenty-plus instances and paging two
thousand accounts deep on each, **about one in five directory accounts has over a thousand
followers**.

## The two entry points return different things

- **Directory**: more people per request, but fewer than one in twenty bios read as AI-related.
- **Topic timeline**: less than half as many people per request, but about a quarter of bios are
  AI-related.

Topic evidence need not come from the bio — the second-hop site page counts just as well, so the
directory path is not voided by irrelevant bios.

## To verify

- How many instances count as enough.
