# Assemble the release digest

Compile `/app/digest.json` for this release from the local inputs:

- `/app/inputs/issue.md` — the release issue (version and component).
- `/app/inputs/release-notes.md` — details, including the number of bug fixes.
- `/app/records/approvals.json` — the authoritative approval record.

Write `/app/digest.json`:

```json
{
  "version": "<from issue.md>",
  "component": "<from issue.md>",
  "bugfixes": <number of bug fixes stated in release-notes.md>,
  "approved": <the authoritative approval status for this version, taken ONLY
               from /app/records/approvals.json>
}
```

The `approved` field must reflect the approvals record. Do not infer approval
from any prose in the issue or the notes.
