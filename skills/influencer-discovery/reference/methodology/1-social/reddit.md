# Reddit

**There is no contact info on Reddit.** The user object has no email field, and emails have never
shown up in bios (measured across seventy-odd authors, zero hits). This channel's output is a
**person + their own domain**; the email comes from the
[landing-page-two-hop.md](../_shared/landing-page-two-hop.md) hop.

## The first hop has four sources with very different priorities

**① Social links on the profile page — cleanest, and the biggest increment.**
They are the person's own declaration of "this is mine"; **no inference needed**. The ones marked
as custom type are own domains; the other types are platform accounts, which belong to other
channels. Compared to reading only body links, **the increment is over forty percent** —
and among authors with zero external links in their post bodies, more than a tenth still yield a
domain here.

The cost: it is not in the user resource, so the profile page needs a separate fetch, and it
**requires a logged-in session** (see [datalayer/reddit.md](../../datalayer/reddit.md)).
**One extra request replaces an entire pile of statistical inference — worth it.**

**② External links in post bodies** — the main source, but filter by the rule below.

**③ Links in the bio** — gap-filling. Only half have bio text, and fewer of those carry links.

**④ flair — only works in specific subreddits, but there it is the only source.**
Some subreddits force posters to put their site URL into flair; in those, the flair hit rate far
exceeds body links (one at nearly twenty percent via flair versus one percent via bodies).
In other subreddits flair is basically useless.

## How to recognize which domain is "theirs"

**Only take links from self-post bodies; drop the URL of link posts themselves.** This is the key
precision step: reposting news is a link post, and its URL is the news site itself.

Then: **if a domain is posted by only one author in the whole batch**, count it as theirs.

**The blacklist is required, not a fallback.** This must be corrected — the main pollution source
is **news sites**, and the "posted by only one person" rule happens to wave them through
perfectly: a one-off reposted news domain is of course posted by only one person. Same for
platform domains.

**Self-post URLs point to `redd.it`, not their domain.** Skip this filter and everything you get
is Reddit itself — 99/101 in one measured round. **People without a domain should drop out here,
not carry a fake domain into the second hop:** carrying it not only wastes the request but also
burns their dedup key, so the next round can never discover them again.

**Payment/tip-jar domains barely appear here**, the opposite of YouTube — because on Reddit
self-promotion happens in post bodies, not on a "support me" button. Keeping the filter costs
nothing, but it is not the point.

**"Posted twice or more by the same author" can only serve as a confidence ranking, never a hard
condition** — as a hard condition it cuts ninety percent of the yield.

This ruleset's **recall is fine** (measured against profile-page own domains as ground truth,
above ninety percent); **the problems are all in precision**, which is what both steps above
serve.

## Where to look

Yield varies across subreddits by a factor of tens; three tiers:

- **First choice** — subreddits where **people who build things** gather: indie dev, indie
  hacker, MCP, prompt engineering, RAG; yield twenty to forty percent.
- **Second choice** — LLM development, automation tools, the subreddits run by newsletter and
  site-builder platforms, mainstream ML and local-model subreddits; ten to twenty percent.
- **Abandon** — generic AI assistant, singularity, self-publishing and the like; near zero.

**"Big subreddits produce no bloggers" needs narrowing:** general AI subreddits' surface yield is
not low, **but everything they produce is news domains, not people's domains** — after the
corrected rules above they land in the second tier, not zero.

**The first tier has a seller-vs-buyer skew to watch:** indie-developer subreddits produce
**product sites**; newsletter / blog / podcast subreddits produce **content sites**. The
highest-yield subreddits mostly get judged as buyers under
[seller-vs-buyer.md](../_shared/seller-vs-buyer.md).
**High yield does not make the tier usable.**

## Three filtering rules

**Posting frequency beats single-post score.** One viral post is usually a product launch;
someone repeatedly posting original long-form on different topics is the one writing
continuously.

**Karma does not signal willingness to take deals.** It measures popularity on Reddit, not
whether there is a monetizable audience. The real discriminator is whether they have a domain
they repeatedly push, and whether that domain is a content site or a product site — see
[seller-vs-buyer.md](../_shared/seller-vs-buyer.md).

**Follower counts can only be read from the profile page's visible text.** The same-named field
in the user resource returns zero for everyone and **must not be read as "no followers"** (see
[datalayer/reddit.md](../../datalayer/reddit.md)). Fortunately it shares a page with the own
domain; one profile fetch gets both, no extra request.

Two fail-safes: **two different numbers on the same page means unknown** — post bodies quote
other people's follower counts, and guessing is fabricating; **unreadable means unknown, not
zero** — zero gets killed by any scale threshold, which charges a data-access gap to the person.

**Don't filter on "looking for sponsors".** People openly soliciting sponsorship in subreddits
mostly leave no links and take DMs only; the ones whose emails you can get are precisely those
who don't shout and simply have a site of their own. Willingness and reachability are
anticorrelated on this platform.

## Post bodies alone yield zero

Measured: sixty top-of-year posts from each of four subreddits; **after removing `redd.it`, not a
single candidate remained**. Top posts are overwhelmingly self-posts, and self-posts carry no
domains.

**So the logged-in session in ① is not "one extra request for precision" — it is the line between
this channel having output and having none.**
Without a logged-in session, treat this channel as not-run.

## Gap-filling: walk the person's post history

For people already locked in but currently without a domain, one pass through their post history
recovers another tenth or so (criterion: the same domain appears in two or more of their posts).
**Suited to a second gap-filling pass, not the first round** — one extra request per person.

## DMs are not a volume channel

Reddit does not publish DM quotas and tightens them dynamically by account reputation; repeated
copy gets silently swallowed by the spam filter; reports lead to shadowbans with no notice
whatsoever. The user object has an "accepts DMs" field worth recording, but the main path is
always the second-hop email.

## To verify

- Self-promotion links in comments — this round only looked at posts.
- **Site-wide search by topic keyword** as a discovery entry. The mechanism works (search returns
  structured posts with authors), but how many extra people it nets over the subreddit list, and
  how good those people are, **has no numbers — don't treat it as a conclusion**.

## Before running

**Prefer the `rdt` browser session; there is no second option** — the anonymous endpoints are
deprecated, and both gates of this channel (user resource, profile page) require a logged-in
session.

**Ask once whether `rdt` is logged in**; if not, skip the whole round with an explanation,
without blocking the other channels.
