# X / Twitter

**Discovery requires auth; anonymous cannot do it.** The anonymous API channel was closed in 2023; fetching `x.com/<handle>` without cookies
returns 200, and the Open Graph tags hold display name, handle, and bio text — **no external links, no follower count, no tweets**.
`twitter.com` and `x.com` return the same thing. The topic-to-person step does not exist anonymously.

## Confirmed

**Auth runs on browser cookies, not passwords, and the fetch layer fetches them itself.** `auth_token` + `ct0` are read from
this machine's Chrome with `browser-cookie3` and fed into **twscrape**'s cookie entry point — no username/password,
no email verification code, no manual account adding — when the account pool is empty the fetch layer refills it once itself.

**twscrape does not go to the browser itself; it only accepts what is fed in**, storing it in its own account pool;
later searches take sessions from the pool. **Fetching and holding are two jobs, split across two tools.** **twikit cannot pass X's anti-bot handshake**; with the same cookie, twscrape
returns live results.

A browser not logged into x.com has no `auth_token`, and this cookie set cannot be completed.

**One search gives everything.** Every tweet `search` returns inlines the full author object:

```
username · displayname · rawDescription (bio) · descriptionLinks (external links in the bio)
followersCount · friendsCount · statusesCount · location · verified · blue
```

**No profile-page lookup needed** — this is the structural difference from Instagram / TikTok / Threads, whose searches
all give no follower count.

Search supports X's own query syntax (`lang:en`, `min_faves:`, and the like); filter conditions can be written into the query itself.

The same author appears repeatedly within one search (one person, many tweets); dedup cumulatively by `username`.

## Unconfirmed

**Pagination caps, rate limits, and the threshold for being judged automation are all untested.** The cookie belongs to a real person's account;
the cost of tripping detection is that account, not a quota.

## Per-call cost

Free — it rides the account's own session, through no vendor.
