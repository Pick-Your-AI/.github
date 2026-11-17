import unittest
from automation.organization_status import finish, main
import json
import os
import sys
from pathlib import Path
import tempfile
from unittest.mock import patch


class StatusTests(unittest.TestCase):
    def test_projects_only_public_safe_fields_and_distinguishes_publication_failure(self):
        receipt = {'last_merged_observation_at': '2026-01-01T00:00:00Z'}
        result = finish(receipt, {
            'status': 'complete', 'observed_at': '2026-01-02T00:00:00Z',
            'content_sha256': 'a' * 64, 'changed': False,
            'members': ['SYNTHETIC_PERSON'], 'token': 'SYNTHETIC_SECRET',
        }, 'failure')
        self.assertEqual(result['collection_status'], 'complete')
        self.assertEqual(result['publication_step'], 'failure')
        self.assertNotIn('SYNTHETIC', str(result))
        self.assertNotEqual(result['last_merged_observation_at'], result['collection_observed_at'])

    def test_failure_never_claims_new_observation(self):
        result = finish({}, {'status': 'failed', 'observed_at': 'not-a-date', 'detail': 'private'}, 'failure')
        self.assertIsNone(result['collection_observed_at'])
        self.assertNotIn('detail', result)

    def test_finish_recovers_after_start_never_created_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp, 'receipt.json')
            env = {'PYA_RUN_STATUS': str(output), 'PYA_STATE': str(Path(tmp, 'private')),
                   'GITHUB_STEP_SUMMARY': str(Path(tmp, 'summary'))}
            with patch.dict(os.environ, env), patch.object(sys, 'argv', ['status', 'finish', '--outcome', 'failure']):
                main()
            result = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(result['collection_status'], 'not_recorded')
            self.assertEqual(result['publication_step'], 'failure')
            self.assertIsNone(result['started_at'])
            self.assertIn('Public-safe refresh receipt', Path(tmp, 'summary').read_text(encoding='utf-8'))
            output.write_text('{broken', encoding='utf-8')
            with patch.dict(os.environ, env), patch.object(sys, 'argv', ['status', 'finish', '--outcome', 'failure']):
                main()
            self.assertEqual(json.loads(output.read_text(encoding='utf-8'))['collection_status'], 'not_recorded')
