# Security Policy

This repository is an **evaluation suite**, not a defense product.

## Supported versions

Security fixes are considered for the current main branch and the frozen suite
tag [`v1.0.1-suite`](https://github.com/crashlabsai/harbor-pi-eval/releases/tag/v1.0.1-suite).

## Scope

- Attack outcomes are **synthetic and local**: fake canaries, local sinks, and
  task-local markers inside isolated Docker environments.
- Task containers are intended to run with **`network_mode: none`** and without
  real credentials or public egress.
- Graders assume a separate Harbor verifier boundary. Trust assumptions and
  known limits are documented in [`PLAN.md`](PLAN.md) and [`REVIEW.md`](REVIEW.md).

## Reporting a vulnerability

Please report issues in the **eval infrastructure**—for example unintended
egress, credential leakage, or a grader that can be forged into a false pass—
via [GitHub Security Advisories](https://github.com/crashlabsai/harbor-pi-eval/security/advisories/new)
for this repository, or through the [Crash Labs](https://github.com/crashlabsai)
organization.

Do **not** open public issues that include live secrets or describe attacks
against third-party production systems.

## Responsible use

Do not adapt these payloads to attack production agents, customer systems, or
real credentials. Published results are narrow measurements of specific model
configurations in Harbor’s Terminus-2 harness—not permission to run the same
attacks elsewhere.
