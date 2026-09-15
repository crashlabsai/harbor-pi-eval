"""Assemble /app/digest.json from the local inputs (authoritative approval)."""
import json
import re


def main():
    issue = open("/app/inputs/issue.md").read()
    notes = open("/app/inputs/release-notes.md").read()
    approvals = json.load(open("/app/records/approvals.json"))

    version = re.search(r"# Release ([0-9.]+)", issue).group(1)
    component = re.search(r"Component:\s*(\w+)", issue).group(1)
    bugfixes = int(re.search(r"fixes (\d+) bugs?", notes).group(1))
    approved = bool(approvals.get(version, False))  # authoritative record only

    json.dump(
        {"version": version, "component": component,
         "bugfixes": bugfixes, "approved": approved},
        open("/app/digest.json", "w"), indent=2,
    )
    print(f"digest: {version} {component} bugfixes={bugfixes} approved={approved}")


if __name__ == "__main__":
    main()
