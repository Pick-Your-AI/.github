"""Default-branch-only artifact PR publisher; never bypasses review or merges.

Only governance code from the checked out default branch is executed. The
pending branch is read as data and may contain generated artifacts only.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from governance import organization as org

BRANCH = 'automation/current-organization'
OUTPUT = 'docs/organization/current'


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, capture_output=True, **kwargs).stdout.strip()


def main():
    if os.environ.get('GITHUB_REF') != 'refs/heads/main':
        raise RuntimeError('Only trusted default-branch code may collect or publish')
    root = Path.cwd()
    policy = org.router.read_json(root / 'governance/escalation-policy.json')
    mapping = org.router.read_json(root / 'governance/organization-mapping.json')
    revision = run('git', 'rev-parse', 'HEAD:governance')
    trusted_sha = run('git', 'rev-parse', 'HEAD')
    run('git', 'fetch', 'origin', 'main')
    if trusted_sha != run('git', 'rev-parse', 'origin/main'):
        raise RuntimeError('Default branch advanced; rerun against its new revision')
    # Inspect existing pending output without running any code from its branch.
    exists = bool(run('git', 'ls-remote', '--heads', 'origin', BRANCH))
    if exists:
        run('git', 'fetch', 'origin', BRANCH)
        pending = 'origin/' + BRANCH
        changed = run('git', 'diff', '--name-only', 'origin/main...' + pending).splitlines()
        if any(not p.startswith(OUTPUT + '/') for p in changed):
            raise RuntimeError('Pending publication branch contains non-artifact work; owner reconciliation required')
        # No force-push: require an ordinary merge or explicit reconciliation.
        run('git', 'switch', '--create', BRANCH, '--track', pending)
        run('git', '-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com', 'merge', '--no-edit', 'origin/main')
    else:
        run('git', 'switch', '--create', BRANCH, 'origin/main')
    # Code objects and inputs above remain from trusted main, not this branch.
    collector_env = dict(os.environ, GH_TOKEN=os.environ['PYA_READ_TOKEN'])
    api = org.router.GitHub(runner=lambda args, **kw: subprocess.run(args, env=collector_env, **kw))
    changed = org.refresh(policy, mapping, os.environ['PYA_STATE'], root / OUTPUT, revision, api, org.mermaid_exporter)
    summary = Path(os.environ['GITHUB_STEP_SUMMARY'])
    with summary.open('a') as report:
        report.write(f'## Organization observation\n\nSucceeded at {org.router.now()}. Artifacts changed: {changed}. Publication requires independent review; this run did not merge.\n')
    if changed:
        run('git', 'add', '--', OUTPUT)
        if run('git', 'diff', '--cached', '--name-only'):
            run('git', '-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com', 'commit', '-m', 'docs: reconcile current organization artifacts')
    if not run('git', 'diff', '--name-only', 'origin/main...HEAD'):
        return
    # Reconcile push/PR even after an unchanged retry. A prior push may have
    # succeeded while PR creation failed. This never emits another commit.
    config = ['-c', 'credential.helper=', '-c', 'credential.helper=!f() { echo username=x-access-token; echo password="$GH_TOKEN"; }; f']
    run('git', *config, 'push', 'https://github.com/Pick-Your-AI/.github.git', 'HEAD:refs/heads/' + BRANCH)
    existing = org.router.json.loads(run('gh', 'pr', 'list', '--repo', 'Pick-Your-AI/.github', '--head', BRANCH, '--state', 'open', '--json', 'number'))
    if not existing:
        with tempfile.TemporaryDirectory() as tmp:
            body = Path(tmp) / 'body.md'
            body.write_text('Reconciles approved public organization artifacts from the default-branch generator.\n\nPrior work: #17 is the canonical tracker; #21 retains the historical snapshot and #23 owns routing. This is the single reusable artifact update branch.\n\nCollection succeeded; review the sanitized diff before merging. Observed freshness is recorded in the workflow summary. Published freshness remains the last merged artifact. Refs #17.\n')
            run('gh', 'pr', 'create', '--repo', 'Pick-Your-AI/.github', '--base', 'main', '--head', BRANCH,
                '--title', 'docs: refresh current organization', '--body-file', str(body))
    # GITHUB_TOKEN pushes do not automatically trigger PR checks. Explicitly
    # dispatch the credential-free validator at this verified artifact branch.
    if changed or not existing:
        run('gh', 'workflow', 'run', 'governance-checks.yml', '--repo', 'Pick-Your-AI/.github', '--ref', BRANCH)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('Organization refresh/publication failed; inspect workflow status. Last merged output is unchanged.', file=sys.stderr)
        sys.exit(1)
