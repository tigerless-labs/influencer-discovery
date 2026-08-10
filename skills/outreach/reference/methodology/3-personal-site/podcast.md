# Podcast

**The highest-yield chain, and it is free.** One iTunes Search API call handles discovery and feed-finding at once; one more feed fetch yields the email — no page parsing, no key, no cookie anywhere.

## Entry

**iTunes' public search endpoint returns shows by keyword, each result carrying its feed URL.** The "find the RSS from the show's homepage" step does not exist; skip it.

A single query term has a result cap; scale by switching terms, same as everywhere else.

**To break past that cap there is a second leg:** Podcast Index publishes a weekly full-database dump requiring no credentials, filterable offline by title and description across millions of feeds. **But the database has no emails** — it replaces the query cap, not the feed-fetch step. Its API requires registering an account for a key; not taken.

## Getting contact info

```
1. Search keyword → show list (feed URLs included)
2. Fetch feed, read <itunes:owner><itunes:email>; also read the owner attribute of <podcast:locked>
3. Judge whether the address belongs to a person (see below)
4. If absent, fall back to the second hop: the feed carries the show's homepage URL
```

`<podcast:locked>` exists for hosting-provider ownership verification; **a minority of shows filled only it and not owner** — one extra attribute scan in the same XML.

**The second hop fetches exactly two pages: homepage and sponsorship page.** Measured: only these two page types produce emails; crawling any other links yields zero. About 40% can be dug out; another ~10% of homepages are unfetchable.

Apple's directory spec requires the feed to carry an owner email for ownership verification, so **over 70% of shows fill it**; after discarding the ones that don't count, **one show in two yields a usable personal address**.

## Which owner emails do not count

Three classes, judged in descending reliability:

- **Same address across multiple shows** — labels, agencies, podcast companies. **The most reliable criterion**: an email prefix can be disguised, repetition count cannot. A handful of addresses in a batch can cover dozens of shows.
- **Hosting-platform forwarding addresses** — domains like anchor / acast / substack. Belongs to the platform, not the person.
- **Role prefixes** — general rule in [landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

Only a quarter of email domains match the show's homepage domain, **so a domain mismatch is not grounds for exclusion** — individuals on free email providers are the norm.

## Multiple hosts

A podcast often has two or more hosts but only **one** owner email. Assigning it to both hosts is exactly the dedup-by-contact-info mistake. **One feed produces one row**, unless the other host was independently discovered through another channel.

## Stop semantics

Search-type — **consecutive rounds with no new results**. The search endpoint returns query results, not an enumerable directory.

## Dedup key

`(show name, Podcast)`. Not the host's name — one person hosting multiple shows is the norm, and those should be multiple rows.

## Boundaries

- Spotify-exclusive shows **have no public RSS**; the shortcut fails there — fall back to the show page and the second hop.
- A few percent of feeds are unfetchable; log them, do not retry.
- No subscribing, no audio downloads, no transcription.

## Tried and dead — do not retry

- **Other email-bearing feed fields** (`managingEditor`, `webMaster`, `googleplay:email`, `copyright`, `podcast:txt`) **add zero** — every show that fills them also fills owner, without exception.
- **Apple and Spotify show pages** are fetchable but contain no email. podchaser rejects an honest UA.
- **Show-notes emails** are 90% just the owner again; **obfuscated forms** (`name (at) domain`) have a regex false-positive rate too high to use — loosen it and everything is English words, tighten it and only one network's shared address remains.
- These three combined recover under 10% of the gap. **Roughly half of shows have no public path** — it ends there.

## To verify

- Coverage of Chinese/non-English shows in this endpoint. This round ran English terms only.
- Whether Apple's `lookup` endpoint can return episode info key-free, **bypassing the feed fetch** — especially relevant for the feeds that won't fetch.
- A third hop: hosts' personal sites among show-notes outlinks. **Hosting-provider and platform domains must be stripped first**, or they dominate the top of every outlink list.
