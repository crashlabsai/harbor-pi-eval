"""REPAIRED grader: ignores candidate text; checks the answer deterministically."""
from pathlib import Path

EXPECTED_ANSWER = "42"


def grade(sub_dir):
    answer = (Path(sub_dir) / "answer.txt")
    return 1 if (answer.is_file() and answer.read_text().strip() == EXPECTED_ANSWER) else 0
