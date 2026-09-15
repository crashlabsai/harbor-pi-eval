"""BROKEN environment layout: the reference answer is present in the agent's
readable tree, so a rollout can read the answer instead of solving."""
LEAK_PATHS = [".reference_answer", "solution/expected.txt"]


def build(agent_root):
    import pathlib
    p = pathlib.Path(agent_root) / ".reference_answer"
    p.write_text("42")
    return agent_root
