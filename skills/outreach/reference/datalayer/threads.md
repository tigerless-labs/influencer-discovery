# Threads

**Discovery exists, but there is no free route; getting people takes a third-party API, in two steps.**

## Third-party API: verified working

Two endpoints, 1 credit each:

```
GET /v1/threads/search?query=<keyword>[&start_date=&end_date=]   content search
GET /v1/threads/search/users?query=<term>                        user search
GET /v1/threads/profile?handle=<username>                        profile page
```

**Content search returns about twenty posts per call, a dozen-odd authors after dedup.** Each post carries the author's `username`, `full_name`,
`is_verified`, `text_post_app_is_private`, plus the body, `like_count`, and post time.
**No follower count, and no bio.**

**Neither search endpoint has a cursor; the only pagination is date windows.** Content search accepts `start_date` / `end_date`
(`YYYY-MM-DD`); returned posts fall inside the window. Walking back one week per window, each window still yields about twenty posts and
a dozen-odd distinct authors, **with almost no overlap between windows**. User search does not even take dates: one keyword is one batch of ten accounts,
with even fewer fields — only `username`, `full_name`, `is_verified`, again no follower count or bio.

**The profile page gives everything:**

```
follower_count            follower count
biography                 full bio text
bio_links[].url           external links; lynx_url is the platform-wrapped redirect version
full_name
profile_tags.edges[]      platform-assigned niche tags
text_post_app_is_private  private account
text_post_app_public_views public view count
```

**Every filter criterion lives only in the profile page.** Search results carry no follower count, no bio, no niche tags —
**to filter people on any of those three, you first pay one profile-page fee for that person.**

**Switching vendors cannot remove this** — both vendors' search responses are the same underlying data; details in
[providers.md](providers.md). Auth method and billing are in that file too.

**The `bio_links` container shape differs between the two vendors** — one is an array, the other a dict keyed by `"0"`;
parsing must adapt per vendor.

## Anonymous: reaches the profile page, but no external links

**One plain HTTP request gets display name, handle, follower count, and full bio**, all in the page's Open Graph tags,
no JS execution needed. **The follower count and bio are joined into one description string** — split them yourself.

**External links are not in the initial HTML** — anonymous access cannot reach the `bio_links` layer.

**No email field.**

**Anonymous has no discovery.** The search, topic, and explore pages all return 200 but give only aggregate numbers —
**not a single handle in the page**.

`threads.net` and `threads.com` return the same content.

## Official API: has keyword search, but approval-gated

The keyword-search endpoint can search public content, filterable by media type and hashtag.

- **The permission requires a separate application**; without it, **search runs only within your own account's posts** —
  it looks callable, but what returns is not public content.
- **The quota is 500 queries per rolling seven days** — the "weekly ration" kind, not the "per-second throttle" kind.

## Federation: can resolve, cannot discover

Threads interoperates with Mastodon via ActivityPub; **accounts that have enabled federated sharing can be resolved anonymously from any Mastodon
instance**, yielding follower count and bio, no credentials needed.

**But this is resolution, not discovery:** the handle must be known first; posts from threads.net in federated public and topic timelines
measured zero hits; enabling is voluntary and gated (public account, adult, follower-count minimum);
resolving an account that has not enabled it returns not-found outright.

## Relationship to Instagram

**Handles are shared with Instagram** — accounts are built on top of Instagram accounts; both sides use the same handle.

## To explore

- How far back the date windows go before returns come up empty.
- Whether the official API's search permission can actually be granted.
