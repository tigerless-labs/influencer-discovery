# Media

**Multi-author publications with editorial review.** Criterion: **multi-author + has editors + sells ad slots**.

**The targets are its authors, not the publication itself.** The publication offers `editors@` or a submissions inbox — an entry to the page space, not a person's address, and it does not count by the [general rule](../_shared/landing-page-two-hop.md); building rows per site would also collapse hundreds of authors into one row — exactly the false merge [dedup.md](../../../../../docs/design/dedup.md) describes.

The uniform method for this tier is therefore: **get the author list from the publication, then follow each author out to their own site.** The key is `(author, this publication)`, not the domain.

## Last in order because it has the most hops

The first four tiers yield a person and their home base; this tier yields a **byline** — one more hop to reach the person, with the highest mid-chain breakage rate. The only reason it is worth running: **author lists are often directory-type and exhaustible**, while the first four tiers are mostly search-type.

## Have their own file

| Platform | Entry |
|---|---|
| [freeCodeCamp News](freecodecamp-news.md) | sitemap gives all authors in one shot, **directory-type, exhaustible** |
| [HackerNoon](hackernoon.md) | RSS gives author names and handles; **second hop severed at the profile page** |

## Not yet, and where each is stuck

**Every line is a measured conclusion, not a guess.**

| Platform | Blocker |
|---|---|
| Towards Data Science | unexplored |
| The New Stack · InfoQ · DevOps.com · SD Times | unexplored |
| VentureBeat · TechCrunch · The Register · Ars Technica · ZDNet | unexplored; general tech media, authors mostly staff journalists |
| Unite.AI · The AI Journal | unexplored |

**Staff journalists are not targets** — their audience belongs to the publication, not to them, and leaves with the job. Freelancers are. This tier's seller-vs-buyer test gains one extra clause: **do they have a home base of their own**.

## Not in this tier

- **Non-profits that sell no page space** still belong here — "sells ad slots" in the criterion is a feature for recognizing media, not an admission requirement. freeCodeCamp is exactly this.
- **Writing platforms without editorial review** go to [2-blog-platform/](../2-blog-platform/index.md).
- **Single-author self-hosted sites** go to [3-personal-site/](../3-personal-site/self-hosted.md).

## Boundaries

Publication domains sit in the shared-domain list in `config/`; **they block row creation only, not citation** — article links can still serve as discovery leads.

## To verify

- **Staff-journalist share.** Decides whether this tier is worth running at all; never measured.
- The three-hop breakage rate when using media author pages as a discovery source.
