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

## Required GitHub repository settings

Maintainers must configure settings that files cannot enforce:

1. **Actions / General:** set workflow permissions to “Read repository contents and packages”; disallow approval bypass. Allow only GitHub-authored, verified required actions, plus the SHA-pinned `astral-sh/setup-uv` and `gitleaks/gitleaks-action` used here.
2. **Rules / Rulesets:** protect `main`; require pull requests, CODEOWNER approval, resolved conversations, linear history, branches up to date, and all checks from CI, Migrations, CodeQL, and Security. Block force pushes/deletion.
3. **Code security:** enable dependency graph, Dependabot alerts/security updates, CodeQL default/setup as appropriate, secret scanning, and push protection. Review dependency audit failures for reachability; document any time-bounded exception rather than silently suppressing it.
