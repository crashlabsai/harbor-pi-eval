# Security

This repository is an **evaluation suite**, not a defense product.

## Scope

- Attack outcomes are **synthetic and local**: fake canaries, local sinks, and
  task-local markers inside isolated Docker environments.
- Task containers are intended to run with **`network_mode: none`** and without
  real credentials or public egress.
- Graders and verifiers assume a separate Harbor verifier boundary; see
  `PLAN.md` and `REVIEW.md` for trust assumptions and known limits.

## Reporting

If you find a vulnerability in the eval infrastructure (for example, unintended
egress, credential leakage, or a grader that can be forged into a false pass),
please open a private report via GitHub Security Advisories for this repository,
or contact the maintainers through the Crash Labs GitHub organization.

Please do **not** file public issues that include live secrets or exploitation
against third-party systems.

## Responsible use

Do not adapt these payloads to attack production agents, customer systems, or
real credentials. The published results are narrow measurements of specific
model configurations in Harbor's Terminus-2 harness—not permission to deploy
the same attacks elsewhere.
