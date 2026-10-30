"""Synthetic publication transport; specifically exercises retry after push."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from automation import publish_organization as publisher


class PublisherTests(unittest.TestCase):
    def test_orphaned_branch_gets_pr_even_when_observation_unchanged(self):
        calls = []
        def run(*args, **kwargs):
            calls.append(args)
            if args[:3] == ('git', 'rev-parse', 'HEAD:governance'): return 'tree'
            if args[:2] == ('git', 'rev-parse'): return 'same-head'
            if args[:2] == ('git', 'ls-remote'): return 'existing'
            if args[:3] == ('git', 'diff', '--name-only'): return publisher.OUTPUT + '/organization.json'
            if args[:3] == ('gh', 'pr', 'list'): return '[]'
            if args[:3] == ('gh', 'run', 'list'): return '[]'
            return ''
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {'GITHUB_REF': 'refs/heads/main', 'PYA_READ_TOKEN': 'synthetic', 'PYA_STATE': tmp, 'GITHUB_STEP_SUMMARY': str(Path(tmp, 'summary'))}):
                with patch.object(publisher, 'run', side_effect=run), patch.object(publisher.org.router, 'read_json', return_value={}), patch.object(publisher.org, 'refresh', return_value=False):
                    publisher.main()
        self.assertTrue(any(c[:3] == ('gh', 'pr', 'create') for c in calls))
        self.assertFalse(any('commit' in c for c in calls))
        self.assertTrue(any(c[:3] == ('gh', 'workflow', 'run') for c in calls))

    def test_never_executes_from_pr_ref(self):
        with patch.dict(os.environ, {'GITHUB_REF': 'refs/pull/123/merge'}), patch.object(publisher, 'run') as run:
            with self.assertRaises(RuntimeError): publisher.main()
            run.assert_not_called()

    def test_moved_default_branch_rejected_before_collection(self):
        def run(*args):
            return 'before' if args == ('git', 'rev-parse', 'HEAD') else 'after'
        with patch.dict(os.environ, {'GITHUB_REF': 'refs/heads/main'}), patch.object(publisher, 'run', side_effect=run), patch.object(publisher.org.router, 'read_json', return_value={}), patch.object(publisher.org, 'refresh') as refresh:
            with self.assertRaises(RuntimeError): publisher.main()
            refresh.assert_not_called()
