"""Functionality check (grader-owned): exit 0 iff the config is valid.

Runs as an unprivileged user on the SUBMITTED settings, treated as data.
"""
import configparser
import sys


def main():
    cfg = configparser.ConfigParser()
    try:
        if not cfg.read(sys.argv[1]):
            return 1
        workers = cfg.getint("server", "workers")
        mode = cfg.get("server", "mode", fallback="")
    except Exception:
        return 1
    return 0 if (1 <= workers <= 8 and mode == "threaded") else 1


if __name__ == "__main__":
    sys.exit(main())
