# Branch Protection Policy

Required status checks (enable in Settings → Branches → Branch protection rules):

- E2E (Playwright) — must pass
- Run backend unit tests (coverage gate) — must pass (cov ≥ 75%)

Other recommendations:
- Require pull request reviews (at least 1)
- Dismiss stale approvals when new commits are pushed
- Require status checks to pass before merging
- Restrict who can push to matching branches (optional)

