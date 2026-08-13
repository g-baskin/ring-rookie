# Contributing

Use Python 3.12+, `uv`, and Node 22. Install with `make install`. Before opening a pull request run:

```sh
make backend-ci
make frontend-ci
make env-check
# With disposable PostgreSQL and DATABASE_URL configured:
make migration-check
# With gitleaks installed and network access:
make security-check dependency-check
```

`make ci` runs every gate. `make clean` removes generated artifacts only. Database volumes are removed only by `make reset-database CONFIRM_RESET=yes`.

`backend/tests/ci-known-failures.txt` temporarily deselects the 17 legacy failures exposed when CI was introduced. CI runs every other test and enforces the measured 37% coverage baseline; delete entries as defects are repaired, and never add one without a tracked issue and owner.

## Required GitHub repository settings

Maintainers must configure settings that files cannot enforce:

1. **Actions / General:** set workflow permissions to “Read repository contents and packages”; disallow approval bypass. Allow only GitHub-authored, verified required actions, plus the SHA-pinned `astral-sh/setup-uv` and `gitleaks/gitleaks-action` used here.
2. **Rules / Rulesets:** protect `main`; require pull requests, CODEOWNER approval, resolved conversations, linear history, branches up to date, and all checks from CI, Migrations, CodeQL, and Security. Block force pushes/deletion.
3. **Code security:** enable dependency graph, Dependabot alerts/security updates, CodeQL default/setup as appropriate, secret scanning, and push protection. `security/dependency-audit-baseline.json` records the pre-existing advisory backlog: CI reports all active findings, fails on new advisory IDs, and announces resolved IDs so maintainers can shrink the baseline. Never add an advisory without a documented reachability review, owner, and expiry.
