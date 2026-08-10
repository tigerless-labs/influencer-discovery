# Mastodon

**There is no auth gate.** Accounts, discovery, and topic timelines are all anonymously fetchable — no key, no cookie.
Currently the only social platform where both discovery and fetching are gate-free.

## Capability boundary

**Discovery exists, with two independent entry points.** One is the account directory endpoint — sorted by activity or newest, pageable,
local and federated both; the other is topic timelines — fetch recent posts by hashtag, then collapse to authors.
Neither needs a seed.

**The two entry points page in different shapes.** The directory jumps by `offset`, at most 80 accounts per page; a large instance still returns full pages at offset twenty thousand,
with no cap observed; topic timelines cursor backward by `max_id`, at most 40 posts per page.

**Topic-timeline posts embed the full account object** — collapsing to authors needs no extra request.

**Three of the returned account fields exist nowhere else:**

- **`fields`** — user-filled key-value pairs, four at most; where they hang their own website.
- **`fields[].verified_at`** — **proof of ownership**. Only when that URL's page links back to the account with `rel="me"`
  does the instance stamp the link with a verification timestamp. **This is the platform's own ownership check, not self-declaration.**
- **`followers_count`** — public, no extra request needed.

`note` is the bio; its content is an HTML fragment, not plain text.

**No email field.** No email slot exists anywhere in the account object.

**Accounts can switch off their own exposure.** There are `discoverable` and `indexable` booleans;
switched-off accounts do not appear in the directory endpoint — the directory is not exhaustive.

**`verified_at` is a minority.** Under a fifth of directory-returned accounts carry the verification stamp; close to seventy percent have a link hung in `fields`.

## Rate and availability

**300 requests per IP per five minutes**; the remaining allowance is in the `X-RateLimit-*` response headers, returned even without auth.

**Not every instance opens its directory anonymously.** The same endpoint returns an HTTP error outright on some instances —
verify the instance list one by one for availability; do not assume uniformity.

## One boundary federation brings

**There is no whole-network view.** Each instance sees only the part of the network it knows,
so the same query returns different results on different instances — **dedup must be done across instances**.
An account's full identifier is `username@instance-domain`; the username alone collides.

**Instances overlap little.** Two pages each from ten instances: accounts appearing more than once were about one sixth —
one more instance is essentially one more batch of people.

## To explore

- How many instances need covering before coverage counts as enough.
