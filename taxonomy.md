# PI task taxonomy

Axes used to classify indirect prompt-injection tasks in this repo. The goal is
to make mechanism overlap explicit so added families are genuinely distinct, not
payload paraphrases (PLAN.md section 4).

## Axes
- **Untrusted surface**: where the attacker text enters the agent's context
  (retrieved document body, commit metadata, tool/diagnostic output, test-case
  name, third-party skill doc, API error field, multi-hop document chain).
- **Attacker outcome class**: exfiltration to a local sink, unauthorized remote
  change, security-setting disablement, protected-state deletion, false claim in
  a deliverable, persistence hook, audit disablement.
- **Evidence channel**: sink-owned journal, captured config parsed as data,
  isolated behavioural test, final-state comparison against an authoritative
  record.
- **Utility coupling**: independent (the job can succeed alongside the unwanted
  action) vs contaminating (attack success invalidates the deliverable).
- **Temporal scope**: end-state only vs "ever happened" (journal-backed).

## Admitted / candidate families
| Family | Surface | Outcome class | Evidence | Utility coupling |
|---|---|---|---|---|
| `vendor-support` (M1) | Vendor doc body | Exfiltration to local sink | Sink journal + canary | Independent |
| `release-remote` | Commit metadata | Unauthorized remote change | Captured git config | Independent |
| `diagnostic-config` | Diagnostic output | Auth setting disabled | Isolated config check | Independent |
| `migration-archive` | HTML guide | Protected records deleted | Final-state compare | Independent |
| `test-name-disclosure` | Test-case name | Secret copied to deliverable | Artifact scan | Independent |
| `vendored-skill` | Skill doc | Persistence hook installed | Shell-config marker | Independent |
| `api-error-audit` | API error field | Audit collection disabled | Sink control journal | Independent |
| `release-approval-chain` | Multi-hop docs | False approval claim | Authoritative record | Contaminating |

Only `vendor-support` is implemented and admitted in M1. The rest are locked
design candidates pending their own admission evidence (PLAN.md section 8).
