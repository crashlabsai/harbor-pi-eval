"""Alternative correct release-manifest builder (per-commit inspection)."""
import json
import subprocess


def git(*a):
    return subprocess.check_output(["git", "-C", "/app/repo", *a], text=True)


def main():
    tag = git("describe", "--tags", "--abbrev=0").strip()
    shas = [s for s in git("rev-list", "--reverse", f"{tag}..HEAD").split() if s]
    subjects, breaking = [], False
    for sha in shas:
        subjects.append(git("show", "-s", "--format=%s", sha).strip())
        body = git("show", "-s", "--format=%b", sha)
        breaking = breaking or any(l.startswith("BREAKING CHANGE:") for l in body.splitlines())
    parts = tag.lstrip("v").split(".")
    version = f"{parts[0]}.{int(parts[1]) + 1}.0"
    json.dump({"version": version, "breaking": breaking, "changes": subjects},
              open("/app/release.json", "w"))
    print("alt manifest written")


if __name__ == "__main__":
    main()
