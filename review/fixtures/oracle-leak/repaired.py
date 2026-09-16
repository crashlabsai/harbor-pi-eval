"""REPAIRED environment layout: no reference answer in the agent's tree."""


def build(agent_root):
    # Intentionally writes nothing secret into the agent-readable tree.
    return agent_root


# Paths that must NOT appear in the agent-readable tree.
FORBIDDEN = [".reference_answer", "solution/expected.txt", "expected.json"]
