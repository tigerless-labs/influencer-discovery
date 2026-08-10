# HackerNoon

Data access: see [datalayer/public.md](../../datalayer/public.md).

**Discovery works; the second hop is severed.** RSS gives author names and handles key-free; following the handle to the profile page to find their own site, the platform returns a challenge page to crawlers that declare themselves. **No bypassing** — this channel ends here.

## Full chain

```
① RSS                0 requests/person   → 20 items per fetch, dc:creator gives the author name, handle in the link
② Profile page       ✗                   → challenge page, own site unreachable
```

## Dedup key

`(author handle, HackerNoon)`. Handle taken from the article link; unique within the platform.

## Boundaries

- Editorial review, sells ad slots — media by [this tier's criterion](index.md).
- **The author may have a home base elsewhere** — discover them from there, not from here.

## To verify

- Whether the profile-page challenge still blocks once a logged-in data layer is wired up.
- The RSS paging depth, and whether it surfaces the full author set.
