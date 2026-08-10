# Reddit

**`rdt` CLI, verified working.** The anonymous `.json` API was retired 2026-05-28; the no-auth route is gone.
`rdt` reuses the browser session; **it fetches the cookie from the browser itself and stores it in its own credentials file** —
no `browser-cookie3` needed. It also has a status entry point that reports whether you are currently logged in.

**Its subcommands do not cover profile pages.** That hop requires issuing requests yourself, cookie taken from that credentials file —
**the login state reaches the caller's hands; it no longer stays inside the CLI.**

**The login state carries read and write capability alike.** Search, subreddit listings, user profiles, and user posts are the four read entries;
commenting, voting, saving, subscribing are writes. Fetching needs only the four reads.

## What you can get

**Search finds people from topics** — site-wide or scoped to a subreddit, sortable by time window and popularity, returning structured fields.
This is true discovery capability, unlike platforms that can only fetch by known account.

**Posts** carry author, subreddit, score, comment count, body. **External links in the body are obtainable only here** —
user resources do not include them.

**Saved output has more fields than screen output.** The default print is a trimmed structure; what is saved to disk is the platform's raw listing structure,
adding poster flair text, self-post vs. link-post, pinned status, and more.
**Only the saved copy can distinguish self posts from link posts.**

**Users** carry bio text, karma, registration date, whether they accept DMs, and whether their email is verified.
`has_verified_email` is just a boolean; **the response contains no address itself**.

**A user's external links exist only in the profile-page HTML; the user resource cannot fetch them.** The set of user-filled social links
on the profile page is structured data — each with type, address, name, position; no parsing of visible text needed.
**They appear in no field of the user resource** — fetch the profile page separately, about half a megabyte per fetch.

**Follower counts likewise — and the same-named field in the user resource is fake.** It returns zero for every account; checked against a top account
with thirty million karma, still zero — the field exists with no real value, and must not be read as "no followers". The real value is in the profile page's **visible
text**, on the same page as the links, so that half megabyte buys both things at once. **This is the only place where a criterion must be read from visible text**,
because the platform put it in no structured location.

**This gate too requires login to cross.** Anonymous user-resource fetches are refused; anonymous profile-page fetches get a JS challenge shell;
the legacy interface returns a block page; only the same address fetched with login state is the real page.

## One fetching convention

**The same post gets reposted across subreddits, and the same person reposts with varied phrasing.** Duplicates in listings and search results must be
collapsed by author at the fetch layer, or downstream sees N identities of the same person.
