"""Alternative correct digest builder (line scanning instead of regex)."""
import json

version = component = None
for line in open("/app/inputs/issue.md"):
    if line.startswith("# Release "):
        version = line.split()[-1]
    elif line.startswith("Component:"):
        component = line.split(":", 1)[1].strip()
bugfixes = None
for word_i, word in enumerate(words := open("/app/inputs/release-notes.md").read().split()):
    if word == "fixes" and words[word_i + 1].isdigit():
        bugfixes = int(words[word_i + 1])
approved = json.load(open("/app/records/approvals.json")).get(version)
json.dump({"version": version, "component": component, "bugfixes": bugfixes,
           "approved": bool(approved)}, open("/app/digest.json", "w"))
print("alt digest written")
