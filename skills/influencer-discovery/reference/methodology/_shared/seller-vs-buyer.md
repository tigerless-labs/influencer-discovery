# Seller or buyer

**Shared component, not a channel.** A judgment applied after the second hop reaches the landing site and before anything is written to the sheet; common to all channels.

Capturing an email does not mean the person will take a promotion deal. Whether the landing site is a **content site** (has an audience to monetize — seller) or a **product site** (buying traffic themselves — buyer) decides whether the row **enters the sheet**.

**Buyer share ranges from zero to over half depending on channel** — in the Reddit round, most people with captured emails were product founders; among newsletter own-sites there was not a single buyer. **Never carry one channel's prior onto another.**

## Pass the own-domain exclusion first, then judge

Measured, the only two hits with "sponsorship signal and nothing else" were **both tipping domains** — a creator's PayPal link mistaken for their own site.

**That is not the judgment layer's fault; it is upstream's.** Payment/tipping, course communities, scheduling/booking, aggregator short links, and platform-owned subdomains must never enter the "own site" list. The list lives in [landing-page-two-hop.md](landing-page-two-hop.md).

## Three evidence levels

**Level 1: behavioral evidence.** The site has a sponsor/ads/media-kit page, a sponsorship inquiry form, ad slots already showing on the homepage, or the email prefix itself is sponsorship-purposed (`advertise@`, `sponsor@`, `partnerships@`).

**But level-1 evidence cannot decide alone** — the exclusion above must run first. Past the exclusion it is highly reliable: all dozen-plus co-occurrences with other content signals were true sellers.

**Level 2: site form. Two grades here, and only one counts.**

- **Structural signals — scored** — feed tags, running on a newsletter platform, a payment provider's script embedded in the page, monthly prices listed. Countable hard facts: product sites rarely publish feeds, content sites rarely embed checkouts.
- **Keyword signals — not scored** — `subscribe`, `archive`, `pricing`, `sign up`. They appear densely on both site types: nearly every SaaS has a `/blog`, and **a pricing page is not buyer evidence either** — creators selling courses have pricing pages too. Measured on a nearly all-seller sample, pricing pages hit almost 40%.

**Keyword signals only flag "needs a human look" when structural signals are absent; they never enter the score.**

**Level 3: behavioral rhythm on the platform.** Repeatedly posting original content on varied topics is a creator; repeatedly pushing the same product is a founder. A one-off viral hit is almost always a product launch.

## How ties land

Ties are not rare — on the most heterogeneous batch of sites they reach 30%. **Split into two grades, neither of which writes a seller/buyer mark:**

- **No signal on either side** — insufficient information. Fetch one more subpage (`/about`, `/blog`) rather than ruling.
- **Hard signals on both sides** — a true conflict, usually "a creator who also sells their own SaaS". These genuinely are both; mark as both and hand to a human, do not force a binary.

## A trap that must be done in two passes

Sponsorship keywords have a high false-positive rate. **A keyword hit only nominates a candidate; a second fetch for context is required to decide.** Coarse filter and fine judgment are two steps; merging them writes buyers into the sheet as sellers.

## Disposition — this is a gate, not a tag

The verdict decides sheet entry; three outcomes:

- **Seller** — enters the sheet, with evidence source attached.
- **Buyer** — **does not enter the sheet; log only**. They want traffic and will not distribute for us; the address is useless even when captured.
- **Tie** — neither grade above enters the sheet. The true-conflict kind (creator also selling their own SaaS) enters marked both: they have an audience, and that is the admission basis.

Logging a buyer is not discarding — the next round will not re-fetch them. **The cost of a false positive is one wasted fetch, not permanent loss.**
