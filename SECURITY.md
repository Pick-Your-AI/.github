# Security policy — Pick Your AI organization files

This repository maintains shared contribution guidance, governance files, and automation. A vulnerability here can affect multiple Pick-Your-AI repositories. Each affected repository's own security policy and evidence requirements still apply.

## Private reporting

**Do not post vulnerabilities, credentials, private membership records, invitation details, or personal information in public issues, pull requests, comments, or workflow logs.**

1. In the affected repository, check **Security → Report a vulnerability** for GitHub private vulnerability reporting. Use it **only if that private feature is available**; this document does not claim it is enabled.
2. If the repository documents another established private disclosure route, follow that route. The [Research security policy](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/SECURITY.md) describes Research's own process.
3. If no private route is available, contact an organization owner through an **existing private channel**, rather than posting details on a public GitHub profile or issue. This document does not create a new inbox or promise that one is monitored. Preserve sensitive evidence privately until an authorized recipient is available.

For ordinary non-sensitive questions, use [SUPPORT.md](SUPPORT.md). Community conduct reports follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Neither a public support issue nor a conduct report is a substitute for a private vulnerability disclosure.

## Scope and handling

Relevant reports include accidental exposure of secrets or non-public data, unsafe GitHub Actions permissions, untrusted automation execution, and bugs in governance tools that could expose or misroute information.

If an exposure is suspected, stop any reproduction that might spread it. Do not paste or commit samples containing actual sensitive values. Only authorized owners should coordinate any required credential rotation, access revocation, private investigation, or history remediation. Use synthetic fixtures for regression tests and publish only sanitized evidence.

Submitting a report does not authorize a production change, GitHub App installation, workflow dispatch, or changes to organization permissions. Fixes follow the relevant repository's protected pull-request and independent-review process.
