# WordPress.com

**The largest platform in this tier, and it works.** No key, no login; one request yields author identity, their own domain, and the key to a key-free email source, all at once.

## Discover people via the tag feed; author object inlined with posts

```
GET https://public-api.wordpress.com/rest/v1.1/read/tags/<tag>/posts?number=40
```

Each post's `author` gives `name`, `nice_name`, `URL` (their self-entered website), `profile_URL`; the post level adds `site_URL` and `site_name`. **No per-person profile lookups needed.**

- **`author.email` is always `false`** — the platform gives no email on this path.
- 120 posts contained 86 distinct authors; **overlap is low, pagination is worth it**.
- **About 40% of authors have a custom domain in `site_URL`**, which is directly the [second hop](../_shared/landing-page-two-hop.md) landing point; the rest stay on `*.wordpress.com` subdomains.

## Gravatar gives email in one hop

`nice_name` is the Gravatar username; the profile has public JSON, no key:

```
GET https://gravatar.com/<nice_name>.json
```

- **About 70% of names resolve**; the rest 404.
- Of those that resolve, **about 20% carry `emails`** (`[{primary, value}]`) — addresses the person deliberately set public, not guessed — consistent with [only using deliberately published contact info](../_shared/landing-page-two-hop.md).
- Also present: `accounts` (twitter / linkedin / youtube etc.) and `aboutMe`, as social fallback and identity corroboration.
- **There is no reliable `urls` field**; external links fall back to `author.URL` and `site_URL`.

End to end: **roughly one author in eight yields an email within two key-free requests**, without entering the second hop.

## Stop semantics

Search-type — **consecutive rounds with no new results**.

## Dedup key

`(author.nice_name, WordPress.com)`. `nice_name` is unique and stable within the platform, more reliable than the display name — display names are heavily auto-generated gibberish.

## To verify

- **Sample quality.** The tag feed is a latest-first feed, visibly mixed with large numbers of junk accounts — the same disease as DEV.to's "default ordering gives 70% zero-engagement authors". **Whether a sort parameter with engagement or a time window exists is unfound. This is the most important item in this file** — without it, discovery volume is high but the seller/buyer ratio will be ugly.
- Gravatar's 20% `emails` rate was measured only on thirty names from one tag; whether it drops in other verticals.
- The net gain from the 40% custom domains completing the second hop, unmeasured.
