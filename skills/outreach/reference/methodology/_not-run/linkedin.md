# LinkedIn

**Not run.** Capability boundaries in [datalayer/linkedin.md](../../datalayer/linkedin.md) — any one of those three boundaries alone is enough to kill it; this file is the verdict itself, plus what the chain looks like after not running it.

## Solving auth would not make it productive

This is its fundamental difference from [twitter-x.md](../1-social/twitter-x.md), worth spelling out:

- **There is no discovery step.** On X, once auth works, search finds people from topics; here there is no counterpart.
- **"Contact info" is visible only to first-degree connections.** Auth solves whether the profile page is viewable, **not whether the contact info is** — building a connection is a social act, not a technical problem.

Which means even if the data layer someday clears it, the chain's shape does not change: still URL-recording only.

## Its actual role today: second-hop landing point

The LinkedIn rows in the target sheet were carried over from personal sites, GitHub, and article bylines — not discovered on LinkedIn. **Record the profile URL as the contact form; do not parse the page** — this path needs no data layer.

`Contact Method = LinkedIn Message`, `Contact Info` is the profile URL. Like X, it is a path, not a verified-deliverable address.

## To verify

- Whether every LinkedIn row in the sheet is a second-hop landing point. If any were genuinely discovered on LinkedIn, the "no discovery step" premise above needs re-examining.
