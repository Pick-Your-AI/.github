"""Synthetic integration tests of the workflow's actual Bash, without GitHub access.

Run on Linux: python3 -m unittest discover -s tests -v
Requires Bash, jq and PyYAML (pip install -r tests/requirements.txt).
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = yaml.safe_load((ROOT / '.github/workflows/early-contributors.yml').read_text())
STEPS = WORKFLOW['jobs']['early-contributors']['steps']

FAKE_GH = r'''#!/usr/bin/env python3
import json, os, subprocess, sys
from pathlib import Path
a = sys.argv[1:]
data = json.loads(Path('fixture.json').read_text())
with open('calls.jsonl', 'a') as f:
    f.write(json.dumps(a) + '\n')
if a[0] == 'api':
    endpoint = next(x for x in a[1:] if not x.startswith('-'))
    if endpoint.endswith('/issues?state=open&per_page=100'):
        assert '--paginate' in a and '--slurp' in a
        subprocess.run(['jq', '-r', a[a.index('--jq')+1]],
                       input=json.dumps(data.get('issue_pages', [data.get('issues', [])])),
                       text=True, check=True)
        sys.exit(0)
    if endpoint == data.get('fail'):
        sys.exit(1)
    if endpoint not in data['api']:
        sys.exit('unexpected API endpoint: ' + endpoint)
    assert '--paginate' in a, a
    for page in data['api'][endpoint]:
        subprocess.run(['jq', '-r', a[a.index('--jq')+1]],
                       input=json.dumps(page), text=True, check=True)
elif a[:2] in (['issue', 'edit'], ['issue', 'create']):
    Path('reported.md').write_text(Path(a[a.index('--body-file')+1]).read_text())
else:
    sys.exit('unexpected gh command: ' + repr(a))
'''


def pr(login, merged='2026-11-15T23:59:59Z', kind='User'):
    return {'merged_at': merged, 'user': {'login': login, 'type': kind} if login else None}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        gh = self.path / 'gh'
        gh.write_text(FAKE_GH)
        gh.chmod(0o755)
        date = self.path / 'date'
        date.write_text('#!/bin/bash\nif [[ "$*" == "-u +%Y-%m-%d" ]]; then\n'
                        '  echo "$TEST_TODAY"\nelse\n  exec /usr/bin/date "$@"\nfi\n')
        date.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.path) + os.pathsep + os.environ['PATH'],
                        ORG='example', TEAM_SLUG='early-contributors', CUTOFF='2026-11-15',
                        GITHUB_OUTPUT=str(self.path / 'output'), GITHUB_REPOSITORY='example/.github')
        self.fixture = {'api': {
            'orgs/example/repos?per_page=100&type=all': [[{'full_name': 'example/one'}]],
            'repos/example/one/pulls?state=closed&per_page=100': [[]],
            'orgs/example/teams/early-contributors/members?per_page=100': [[]],
            'orgs/example/teams/early-contributors/invitations?per_page=100': [[]],
        }}

    def run_step(self, step_id=None, name=None, success=True):
        step = next(s for s in STEPS if s.get('id') == step_id and step_id or s.get('name') == name and name)
        (self.path / 'fixture.json').write_text(json.dumps(self.fixture))
        result = subprocess.run(['bash', '-c', step['run']], cwd=self.path, env=self.env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def calls(self):
        return [json.loads(line) for line in (self.path / 'calls.jsonl').read_text().splitlines()]

    def test_pagination_beyond_search_cap_and_filtering(self):
        api = self.fixture['api']
        api['orgs/example/repos?per_page=100&type=all'].append([{'full_name': 'example/two'}])
        # 1,200 distinct authors across twelve API pages plus a second repository.
        api['repos/example/one/pulls?state=closed&per_page=100'] = [
            [pr('human' + str(n)) for n in range(i, i + 100)] for i in range(0, 1200, 100)]
        api['repos/example/two/pulls?state=closed&per_page=100'] = [[
            pr('human0'), pr('robotics-human'), pr('applicant'), pr('real-bot-lover'),
            pr('service', kind='Bot'), pr('robot[bot]'), pr('app/service'),
            pr(None), pr('unknown', kind=None), pr('late', '2026-11-16T00:00:00Z'),
            pr('closed-only', None), pr('member'), pr('invited')]]
        api['orgs/example/teams/early-contributors/members?per_page=100'] = [[{'login': 'member'}], [{'login': 'human1'}]]
        api['orgs/example/teams/early-contributors/invitations?per_page=100'] = [[{'login': None}], [{'login': 'invited'}]]
        self.run_step('find')
        candidates = (self.path / 'candidates.txt').read_text().splitlines()
        self.assertEqual(len(candidates), 1202)
        self.assertTrue({'human1199', 'robotics-human', 'applicant', 'real-bot-lover'} <= set(candidates))
        self.assertEqual(len(candidates), len(set(candidates)))
        self.assertEqual((self.path / 'output').read_text(), 'count=1202\n')
        self.assertTrue(all(c[0] == 'api' and '--paginate' in c for c in self.calls()))

    def test_empty_emits_zero(self):
        self.fixture['api']['repos/example/one/pulls?state=closed&per_page=100'] = [[
            pr('automation', kind='Bot'), pr(None), pr('unmerged', None)]]
        self.run_step('find')
        self.assertEqual((self.path / 'output').read_text(), 'count=0\n')

    def test_actual_window_boundary(self):
        self.env['PROJECT_START'] = '2026-10-16'
        self.env['WINDOW_DAYS'] = '30'
        for today, opened in [('2026-11-14', 'true'), ('2026-11-15', 'true'),
                              ('2026-11-16', 'false')]:
            with self.subTest(today=today):
                self.env['TEST_TODAY'] = today
                (self.path / 'output').unlink(missing_ok=True)
                self.run_step('window')
                self.assertEqual((self.path / 'output').read_text(),
                                 'cutoff=2026-11-15\nopen=' + opened + '\n')

    def test_failures_do_not_emit_authorization_count(self):
        for endpoint in self.fixture['api']:
            with self.subTest(endpoint=endpoint):
                self.fixture['fail'] = endpoint
                self.run_step('find', success=False)
                self.assertFalse((self.path / 'output').exists())

    def test_zero_report_exact_existing_or_missing(self):
        name = 'Clear pending additions in an existing issue (dry run)'
        self.fixture['issue_pages'] = [[{'number': 1, 'title': 'Early Contributors: pending additions extra'},
                                        {'number': 9, 'title': 'Early Contributors: pending additions',
                                         'pull_request': {'url': 'synthetic'}}],
                                       [{'number': 2, 'title': 'Early Contributors: pending additions'}]]
        self.run_step(name=name)
        self.assertIn(['issue', 'edit', '2'], [c[:3] for c in self.calls()])
        self.assertIn('No one is pending', (self.path / 'reported.md').read_text())
        first_body = (self.path / 'reported.md').read_text()
        self.run_step(name=name)
        self.assertEqual(first_body, (self.path / 'reported.md').read_text())
        self.assertFalse(any(c[:2] == ['issue', 'create'] for c in self.calls()))
        (self.path / 'calls.jsonl').unlink()
        del self.fixture['issue_pages']
        self.fixture['issues'] = [{'number': 1, 'title': 'Early Contributors: pending additions extra'}]
        self.run_step(name=name)
        self.assertEqual(len(self.calls()), 1)

    def test_positive_report_exact_match(self):
        (self.path / 'candidates.txt').write_text('human\n')
        self.fixture['issues'] = [{'number': 1, 'title': 'Early Contributors: pending additions extra'},
                                  {'number': 2, 'title': 'Early Contributors: pending additions'}]
        self.run_step(name='Report candidates in an issue (dry run)')
        self.assertIn(['issue', 'edit', '2'], [c[:3] for c in self.calls()])
        (self.path / 'calls.jsonl').unlink()
        self.fixture['issues'] = []
        self.run_step(name='Report candidates in an issue (dry run)')
        self.assertIn(['issue', 'create'], [c[:2] for c in self.calls()])

    def test_actual_guard_matrix(self):
        # Evaluate the limited expression syntax used by the actual YAML guards.
        for opened in (False, True):
            for event in ('schedule', 'workflow_dispatch', 'push'):
                for apply in (False, True):
                    for count in ('0', '2'):
                        values = {'steps.window.outputs.open': str(opened).lower(),
                                  'github.event_name': event, 'inputs.apply': apply,
                                  'steps.find.outputs.count': count}
                        actual = []
                        for step in STEPS[3:]:
                            expression = step['if'].replace('&&', ' and ')
                            for key, value in values.items():
                                expression = expression.replace(key, repr(value))
                            actual.append(eval(expression, {'__builtins__': {}}, {}))
                        self.assertEqual(actual, [opened and event == 'workflow_dispatch' and apply and count != '0',
                                                  opened and event == 'schedule' and count != '0',
                                                  opened and event == 'schedule' and count == '0'])


if __name__ == '__main__':
    unittest.main()
