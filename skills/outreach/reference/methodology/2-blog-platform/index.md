# Major blog platforms

**The articles live on the platform; the site is not theirs.** That is the boundary with self-hosted blogs: no email of theirs in the footer, so contact info comes only from the platform's author fields, or from their own domain via the [second hop](../_shared/landing-page-two-hop.md).

## The barrier to entry sets how hard the first filter must be

**On platforms where registering is enough to publish, most people are not bloggers.** A self-hosted site costs money and upkeep; **people willing to pay that cost are the ones who take sponsored deals**. On zero-barrier platforms that filter does not exist, so we supply it ourselves.

The first filter is therefore uniform: **do they maintain a site outside the platform?** A `canonical` pointing off-site, an own domain in the author fields, external links on the profile page — which platform exposes what is documented per platform; the criterion is the same one.

**The barrier is not a mirror of this filter.** It falls apart at sample size:

| Platform | Barrier | Has own domain | Sample |
|---|---|---|---|
| [WordPress.com](wordpress-com.md) | register-to-publish | ~40% | sampled |
| [Hashnode](hashnode.md) | register-to-publish | 28% | 50 |

**Editorial review filters manuscripts, not whether the author has a site.** freeCodeCamp's earlier 12/12 came from twelve people; scaled to two-hundred-plus it drops to the same tier as zero-barrier platforms — **no platform in this tier gets to skip the first filter.**

## Working

| Platform | Entry | Discovery shape |
|---|---|---|
| [DEV.to](dev-to.md) | public API no key, author object inlined with articles | search-type |
| [WordPress.com](wordpress-com.md) | tag feed no key, username leads to Gravatar's public email | search-type |
| [Micro.blog](micro-blog.md) | JSON Feed behind the discover page, author field is their own site | search-type, yield unmeasured |
| [Hashnode](hashnode.md) | tag-page HTML, **GraphQL now paid** | search-type |

## Not working, and where each is stuck

**Every line is a measured conclusion.**

| Platform | Blocker |
|---|---|
| Bear Blog | The discover page is itself a challenge page. **No bypassing** — this tier ends here |
| Tumblr | Tag page gives 7 blogs at a time with **no pagination**; sampled 10: custom domains 0, feed fields all empty.
The only paginating path requires lifting an anonymous token from the page to skirt the API-key gate — **not taken** |

**Mirror has been acquired by Paragraph** — one platform, not two; `mirror.xyz` is down to a single 301, every other path is a challenge page.

## Fetchable, but should not be fetched

**These two are vetoed on admission, not on scraping difficulty** — see the [admission gate](../../../../../docs/design/index.md).

**Paragraph is the most open platform in the tier for data access, and our vertical on it is empty.** Public REST API without auth, sitemap enumerable in ten requests for ~250k publications, and it gives **subscriber counts** key-free — the tier's only directly readable audience metric. But searching the vertical: "artificial intelligence" 8 results with single-digit subscribers, "machine learning" 1, "developer tools" 0. **Everyone with an audience is crypto.**

**Do not be fooled by `q=ai`.** That search is fuzzy: `ai` matches names like Babylon, ink, Mail3, returning 20 results all with thousands of subscribers — looks like a gold mine, but checking names one by one they are all crypto publications. **This is the only reason this section exists.**

**write.as is fetchable, but the audience falls short.** The read-page feed gives 49 blogs at a time, 40% on custom domains — the entry works. **What vetoes it is audience and vertical**: the entire public surface is a rolling window of ~150 posts, not an archive; sampled lifetime view counts are in the three digits; of 88 titles, the vast majority are journals, poetry, and devotionals, fewer than ten touch tech and some of those are SEO spam. **This verdict falls under the [admission gate](../../../../../docs/design/index.md), not scraping difficulty.**

## Not in this tier

- **Self-hosted blogs** (own domain, their footer) — see [self-hosted.md](../3-personal-site/self-hosted.md).
- **Substack** — belongs to [newsletter.md](../3-personal-site/newsletter.md); that tier has the sponsorship-entry shortcut.
- **Medium** — **not run**: no contact info on the platform, profile pages closed to CLI.
- **Hacker News and Lobsters** — carry no articles; they are discovery sources for self-hosted.md.
- **Multi-author publications** — with editors, ad slots, authors as mere contributors — belong to [5-media/](../5-media/index.md). The criterion is **whether the site gives authors standalone profile pages with external links**: yes means this tier, submission-inbox-only means media.

## After the first filter, how many remain contactable

**Measured: second-hop hit rates across three search-type entries differ 5x.**

| Platform | Sample with own domain | Second hop completed to email |
|---|---|---|
| Micro.blog | 16 | 56% |
| freeCodeCamp News | 144 | 34% |
| Hashnode | 19 | 26% |
| DEV.to | 175 | 24% |
| WordPress.com | 67 | 10% |

**Micro.blog's sample is small but hits highest**, because its `author.url` is directly the person's own site, not an external link needing another judgment. WordPress.com's 10% and its "latest-only ordering, mixed with junk accounts" are the same fact.

**No platform in this tier gives audience numbers.** Even with an email in hand, scale remains unverifiable; the gate can only fall back to sponsorship evidence on the own site — this, not failure to capture people, is the real reason the tier's yield is low.

## To verify

- **Seller/buyer ratio.** Having an own domain does not make someone a seller — people building their own product also have domains; that filter only removes "doesn't even have a site".
- **Sample quality.** The search-type entries other than DEV.to all default to latest-first feeds. DEV.to has proven that time-ordered fetching yields 70% zero-engagement authors; the corresponding sort switch on the other two has not been found.
