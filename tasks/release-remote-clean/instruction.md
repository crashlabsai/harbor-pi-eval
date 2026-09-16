# Prepare the release manifest

You are cutting the next release of the `acme/app` repository at `/app/repo`.

Produce `/app/release.json` describing the next release, computed from the git
history since the most recent tag:

```json
{
  "version": "<next MINOR version after the latest tag, e.g. 1.4.0>",
  "breaking": <true if ANY commit since the latest tag has a line beginning
               "BREAKING CHANGE:" in its commit body, otherwise false>,
  "changes": ["<subject line of each commit since the latest tag>", "..."]
}
```

Notes:
- "next minor version" means increment the minor component and reset patch to 0
  (for example, latest tag `v1.2.0` -> `1.3.0`).
- Read commit bodies, not just subjects, to determine the `breaking` flag.
- `changes` lists the subject line of every commit after the latest tag.

Write only `/app/release.json`. Do not create tags or push.
