# LinkedIn

**Auth gets you in, but the discovery step does not exist.** This machine's Chrome has `li_at` (logged in); technically the route works.

## Capability boundary

- **No public people search**; the official API is partner-gated — cannot find people from criteria, only fetch by known
  profile URL.
- **"Contact info" is visible only to first-degree connections.** Auth solves whether you can see the profile page,
  not whether you can see the contact info on it.
- **Automation detection is the strictest anywhere, and bans are irreversible**, while the account is the person's real professional identity.

## The one bit that bypasses the fetch layer

The profile URL itself. It comes along from elsewhere; it needs neither login nor page parsing.
