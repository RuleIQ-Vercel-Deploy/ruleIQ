# Licensing and Usage

This software is proprietary and provided under a restrictive license. All rights reserved.

- Allowed:
  - Internal evaluation, testing, and development within your organization.
- Not allowed without a separate commercial agreement:
  - Production use
  - Commercial use
  - Redistribution (public or private)
  - Modification and creation of derivative works
  - Sublicensing, sale, leasing, or hosting as a service for third parties
  - Benchmarking or publishing performance results (unless required by law)

See the full terms in the repository root [LICENSE](../LICENSE).

## Commercial Licensing

For production, commercial, or broader rights, please contact:
- legal@ruleiq.com

Provide your company name, intended use, deployment environment(s), and timeline.

## CI Guard for Public Publication

This repository includes a publication guard workflow to prevent accidental public releases under a permissive license.

- Workflow: .github/workflows/publish-guard.yml
- Trigger: on GitHub Release events (created/published)
- Behavior: Fails unless the GitHub secret `LICENSE_APPROVED` is set to the string `"true"`

To allow a controlled public release (e.g., private preview or licensed distribution):
1. Have legal approve the release.
2. In repository settings, add a secret `LICENSE_APPROVED` with value `true`.
3. Re-run the release workflow, or create a new release.

To integrate the guard in new publish workflows (npm/PyPI/etc.), add a reusable call:

```yaml
jobs:
  license-guard:
    uses: ./.github/workflows/publish-guard.yml
```

Then place your publish job with `needs: [license-guard]`.

## Frontend Package License

The frontend package.json sets `"license": "UNLICENSED"`, ensuring package managers do not infer accidental permissive licensing.

## Badge and Documentation Alignment

- README badge shows a Proprietary license.
- Any external docs and marketing materials should reference the proprietary license and commercial licensing path above.

If you have questions about these terms, contact legal@ruleiq.com.