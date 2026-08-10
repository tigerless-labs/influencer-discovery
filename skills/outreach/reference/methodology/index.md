# Channel methodology

Once the data is in hand: **which page the contact info lives on, and which entry point to use**.
How to fetch data is in [datalayer/](../datalayer/index.md); the two are kept separate: that side
only documents each platform's **capability boundary**; **whether to run it is decided here**,
and so is how to get the contact info.

**Who counts as a target is not decided here** — the three-tier admission rule (people with an
audience / sites that do distribution / people building their own product stay off the sheet) is
design, see [docs/design/index.md](../../../../docs/design/index.md). This side only documents how
each channel applies it.

## Directory order is priority

Collaboration priority is carried by the numeric prefix of the directory name;
**the prose does not maintain a second ranking**.

**The line between the two blog tiers is a barrier to entry, not a format.** Buying your own
domain, building your own site, and maintaining it costs money and effort;
**only people willing to pay that cost treat writing as a business** — and those are exactly the
people who take sponsored deals. Platforms where anyone can sign up and publish have no such
filter; most people there have merely published a few posts — they are not bloggers.

| Directory | What it is | Channels |
|---|---|---|
| `_shared/` | Shared components, not a channel | Second hop · seller-vs-buyer test · cost ranking |
| `1-social/` | Major social media | X · TikTok · Instagram · Threads · YouTube · Reddit · Mastodon |
| `2-blog-platform/` | Articles published on a platform; the site is not theirs | [List in its own index](2-blog-platform/index.md) |
| `3-personal-site/` | **Has a barrier**: own domain, self-grown audience | Self-hosted blog · Newsletter · Podcast |
| `4-distribution/` | Sites that do distribution; the output is a submission entry point, not a person | Website |
| `5-media/` | **Multi-author publications with editorial review**: the targets are their authors, not the publication | [List in its own index](5-media/index.md) |
| `_not-run/` | Not run | LinkedIn |

## Shared components

- [landing-page-two-hop.md](_shared/landing-page-two-hop.md) — platform page → the person's own
  site → contact page; the common second half of every channel. **General rules for noise and
  "addresses that don't count" live here; channels only document their own exceptions.**
- [seller-vs-buyer.md](_shared/seller-vs-buyer.md) — whether the landing site is a content site or
  a product site, **which decides whether the row goes on the sheet**. The last gate before writing
  to the sheet.
- [cost-ranking.md](_shared/cost-ranking.md) — how to choose among multiple paths: free ones rank
  ahead of paid ones; among paid ones, efficiency beats unit price.

## Proven

**Every figure is backed by a real run.**

Free, no credits burned:

- [podcast.md](3-personal-site/podcast.md) — **highest yield**: one key-free search → feed → email,
  no page parsing
- [newsletter.md](3-personal-site/newsletter.md) — the category endpoint is **directory-type and
  exhaustible**; the feed provides the address
- [self-hosted.md](3-personal-site/self-hosted.md) — four key-free discovery sources with
  complementary biases; use them crosswise
- [2-blog-platform/](2-blog-platform/index.md) — all five platforms in the tier work, all key-free.
  **freeCodeCamp News is the only directory-type exhaustible one among them**
- [youtube.md](1-social/youtube.md) — under one in ten bios give an email directly; yield comes
  from the links section
- [website.md](4-distribution/website.md) — takes submission entry points, not people

Through the paid data layer:

- [instagram.md](1-social/instagram.md) — one step: search results carry bio, external link, and
  follower count directly
- [tiktok.md](1-social/tiktok.md) — two steps; highest rate of emails directly in the bio
- [reddit.md](1-social/reddit.md) — no contact info on the platform; the output is a person +
  their domain
- [threads.md](1-social/threads.md) — two steps; filtering only possible after fetching the
  profile page

## Decided to run, numbers untested

The method is written in the shape of the proven channels; **the steps in the prose are usable,
but not a single hit rate has been measured** — run one round before relying on it; each file's
"To verify" section lists which numbers to measure first.

- [mastodon.md](1-social/mastodon.md) — **own domain requires no inference**: the platform does
  attribution verification itself; key-free and login-free
- [twitter-x.md](1-social/twitter-x.md) — topic search can find people; data access goes through
  the user's own account
- [micro-blog.md](2-blog-platform/micro-blog.md) — the JSON Feed behind the discovery page is
  key-free; `author.url` is the person's own site directly

## Not run

- [linkedin.md](_not-run/linkedin.md) — **no discovery step exists**, and authentication doesn't
  buy one; also covers how to fetch once it is done and how not doing it shapes this chain.

## Deleted

No yield for the goal of "finding bloggers who can do distribution"; original text is in git
history:

- **Sponsorship marketplaces** (Passionfroot / Paved) — the directory requires an account;
  historical links are the only source of handles, and six in ten are already 404, so it decays to
  zero naturally.
- **Medium** — no contact info on the platform; profile pages are closed to CLI.
- **GitHub** — people there are mostly founders and self-builders, not distributors.
  Still useful as a **second-hop landing point**; the method lives in tier ④ of
  [landing-page-two-hop.md](_shared/landing-page-two-hop.md).

Not written: Product Hunt. Left empty.
