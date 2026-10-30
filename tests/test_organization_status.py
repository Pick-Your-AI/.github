import unittest
from automation.organization_status import finish


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
