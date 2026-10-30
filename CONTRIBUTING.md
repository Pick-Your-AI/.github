# Contributing to Pick Your AI

This page sets the access, branch, review and merge rules for every Pick-Your-AI repository. Each repository's own CONTRIBUTING.md adds its workflow, checks and evidence rules, and links back here.

## Roles

| Role | Who | What you can do |
| --- | --- | --- |
| Contributor | Anyone with a GitHub account | Fork a repository, open issues, and open pull requests from your fork. |
| Early contributor | Members of the `early-contributors` team | Write access to `pick-your-ai-research`, `pick-your-ai-website`, `pick-your-ai-leaderboard`, `pick-your-ai-android` and `pick-your-ai-apple`; read access to `.github`. You can push branches under `contrib/`, open issues and pull requests, and review pull requests. You cannot push to `main` or to other branches, create or move tags, or merge. |
| Maintainer | The repository's maintainer team | Push any branch, and merge approved pull requests. |
| Organization admin | Organization owners | Everything above. Admins can also bypass the review requirement. Reserve this for emergencies and explain the bypass in the pull request. |

Repository access is granted to teams, not individuals. Ask an organization admin for changes.

## Teams and access

Current area, specialist and lead-team names are listed in the [organization naming register](docs/NAMING.md). The top-level team is `Organization Maintainers`; its area teams include `Research`, `Mobile Apps`, `Websites` and `Education`. Repository teams include `AI Builder`, `Main Website`, `Contributor Leaderboard`, `AI Applications`, `Android` and `Apple/iOS`. Lead-team names use `Lead Maintainers - <Area>`.

GitHub team/repository grants remain authoritative for access. Parent Triage, repository Write and lead-team Admin are distinct grants; a team name does not itself grant permissions. The naming alignment preserves memberships, team-manager roles, parent relationships and repository/Project grants, including existing exceptions and interim coverage. `Early Contributors`, `Review Leads` and `Research Maintainers` retain their separate roles.

Team membership and settings are managed by organization owners and the relevant team's designated GitHub maintainers. The [accepted delegation record](https://github.com/Pick-Your-AI/.github/issues/18) distinguishes that role from repository Admin access and operational ownership. Do not infer an assignment from a name or membership. Organization-file changes still require a pull request and the applicable review rules; naming changes do not expand anyone's access.

## Workflow for early contributors

You do not need a fork.

```sh
gh auth login                                    # or add an SSH key to your GitHub account
git clone git@github.com:Pick-Your-AI/<repo>.git
cd <repo>
git switch -c contrib/<your-login>/<topic> origin/main
# commit your changes
git push -u origin HEAD
gh pr create --base main
```

- Push only to branches that start with `contrib/`. Pushes to other branches are rejected. Maintainers and Dependabot use their own branch names.
- Other contributors can also push to `contrib/` branches. Only push to your own branches.
- Follow the repository's CONTRIBUTING.md for issue linking, checks and evidence.

If you are not an early contributor, fork the repository, push your branch to the fork, and open the pull request from there.

## Reviews and merging

- Every pull request into `main` needs one approval from someone other than its author.
- If anyone pushes after the approval, someone other than the person who pushed must approve again.
- Any approval from someone with write access counts. Only maintainers and admins can merge.
- Maintainers merge with **Merge without waiting for requirements to be met (bypass rules)**, or `gh pr merge --admin`. This skips only the branch restrictions; the approval is still required, as are the required checks where a repository enforces them (`ci-required` in `pick-your-ai-website`).
- Nobody except an organization admin can push directly to `main`.

## Credentials

- Use your own account through `gh auth login` or an SSH key. Never share keys or tokens, and never paste them into issues, pull requests or logs.
- The organization allows only approved OAuth apps.
- Fine-grained personal access tokens need admin approval. Request only what you need: the specific repositories, **Metadata: read**, and **Contents**, **Issues** or **Pull requests: write** as required. Do not request organization permissions. Requests outside this policy are denied.

## Actions and deployments

- Workflows can use only GitHub-owned actions (`actions/*`).
- Workflows on contributor branches run without access to deployment secrets. The `pick-your-ai-website` `production` environment accepts only `main`.
- `pick-your-ai-website` deploys automatically when a pull request merges into `main`. Manual redeploys, rollbacks and re-runs of old deploys run only for logins in the admin-managed `DEPLOY_DISPATCHERS` repository variable.

## Where the rules are enforced

Each repository has these rulesets. If you change them, update this page in the same change.

| Ruleset | Effect |
| --- | --- |
| Contributor boundary: default branch | Only maintainers and admins can update, delete or force-push `main`. |
| Contributor boundary: branches | Branches outside `contrib/` and `dependabot/` are maintainer-only. |
| Contributor boundary: tags | Only maintainers and admins can create, move or delete tags. |
| Review required: default branch | One approval, and approval of the most recent push, before merging into `main`. Only organization admins can bypass it. |

`pick-your-ai-website` and `pick-your-ai-research` also keep their earlier `main` rulesets, which require a pull request and block deletion and force pushes. `pick-your-ai-website` also requires the `ci-required` check.
