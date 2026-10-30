"""Synthetic adapter tests: no webhook subscription or live API is used."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepared_trigger', ROOT / 'automation/refresh_trigger.py')
trigger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trigger)
fixture_spec = importlib.util.spec_from_file_location('routing_fixtures', ROOT / 'tests/test_router.py')
fixtures = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixtures)


class TriggerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.secret = 'synthetic-webhook-secret'
        env = patch.dict(os.environ, {'PYA_WEBHOOK_SECRET': self.secret})
        env.start()
        self.addCleanup(env.stop)
        self.config = fixtures.policy()
        self.args = {name: self.root / (name + '.json') for name in ('payload', 'policy', 'snapshot', 'status', 'ledger')}
        self.args.update(event='membership', delivery='fixture-delivery-1')
        self.args['policy'].write_text(json.dumps(self.config))
        self.sign({'action': 'added', 'organization': {'id': 100}, 'scope': 'team'})
        self.calls = []

    def sign(self, value):
        body = json.dumps(value).encode()
        self.args['payload'].write_bytes(body)
        self.args['signature'] = 'sha256=' + hmac.new(self.secret.encode(), body, hashlib.sha256).hexdigest()

    def refresh(self, config, snapshot, status):
        self.calls.append((config, snapshot, status))

    def process(self, **changes):
        return trigger.process(**(self.args | {'refresh': self.refresh} | changes))

    def ledger(self):
        return json.loads(self.args['ledger'].read_text())

    def test_supported_events_and_actions(self):
        for event, actions in trigger.SUPPORTED.items():
            for action in actions:
                with self.subTest(event=event, action=action):
                    value = {'organization': {'id': 100}}
                    if action is not None:
                        value['action'] = action
                    self.sign(value)
                    delivery = f'fixture-{event}-{action}'.replace('_', '-')
                    self.assertEqual(self.process(event=event, delivery=delivery)['status'], 'succeeded')
        self.assertEqual(len(self.calls), 8)

    def test_org_event_and_signature_rejections(self):
        for value, event, status in [
            ({'action': 'added'}, 'membership', 'organization_invalid'),
            ({'action': 'added', 'organization': {'id': 999}}, 'membership', 'organization_mismatch'),
            ({'action': 'added', 'organization': {'id': True}}, 'membership', 'organization_invalid'),
            ({'action': 'unknown', 'organization': {'id': 100}}, 'membership', 'event_unsupported'),
            ({'action': 'added', 'organization': {'id': 100}}, 'push', 'event_unsupported'),
        ]:
            with self.subTest(status=status):
                self.sign(value)
                with self.assertRaisesRegex(trigger.TriggerError, '^' + status + '$'):
                    self.process(event=event)
        with self.assertRaisesRegex(trigger.TriggerError, 'signature_invalid'):
            self.process(signature='sha256=' + '0' * 64)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.args['ledger'].exists())

    def test_missing_secret_malformed_json_and_team_add_action(self):
        with patch.dict(os.environ, {'PYA_WEBHOOK_SECRET': ''}):
            with self.assertRaisesRegex(trigger.TriggerError, 'secret_missing'):
                self.process()
        self.sign({'organization': {'id': 100}, 'action': None})
        with self.assertRaisesRegex(trigger.TriggerError, 'event_unsupported'):
            self.process(event='team_add')
        body = b'{malformed'
        self.args['payload'].write_bytes(body)
        self.args['signature'] = 'sha256=' + hmac.new(self.secret.encode(), body, hashlib.sha256).hexdigest()
        with self.assertRaisesRegex(trigger.TriggerError, 'payload_invalid'):
            self.process()
        self.assertEqual(self.calls, [])

    def test_dedup_and_changed_payload_or_event_conflict(self):
        self.assertEqual(self.process()['status'], 'succeeded')
        self.assertEqual(self.process()['status'], 'duplicate_succeeded')
        self.assertEqual(len(self.calls), 1)
        with self.assertRaisesRegex(trigger.TriggerError, 'event_unsupported'):
            self.process(event='team')
        self.sign({'action': 'removed', 'organization': {'id': 100}})
        with self.assertRaisesRegex(trigger.TriggerError, 'delivery_conflict'):
            self.process()

    def test_failure_retry_bounded_and_success_not_fabricated(self):
        def fail(*_):
            raise RuntimeError('PRIVATE TOKEN MUST NOT ESCAPE')
        for attempt in range(1, 4):
            with self.assertRaisesRegex(trigger.TriggerError, '^refresh_failed$'):
                self.process(refresh=fail, retry_failed=attempt > 1)
            record = self.ledger()['deliveries']['fixture-delivery-1']
            self.assertEqual((record['state'], record['attempts']), ('failed', attempt))
            self.assertNotIn('PRIVATE', self.args['ledger'].read_text())
        with self.assertRaisesRegex(trigger.TriggerError, 'retry_requires_explicit_flag'):
            self.process()
        with self.assertRaisesRegex(trigger.TriggerError, 'retry_exhausted'):
            self.process(retry_failed=True)

    def test_failed_then_success(self):
        with self.assertRaisesRegex(trigger.TriggerError, 'refresh_failed'):
            self.process(refresh=lambda *_: (_ for _ in ()).throw(RuntimeError()))
        self.assertEqual(self.process(retry_failed=True)['status'], 'succeeded')
        self.assertEqual(self.ledger()['deliveries']['fixture-delivery-1']['attempts'], 2)

    def test_pending_crash_requires_reconciliation(self):
        def crashed(*_):
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            self.process(refresh=crashed)
        self.assertEqual(self.ledger()['deliveries']['fixture-delivery-1']['state'], 'pending')
        with self.assertRaisesRegex(trigger.TriggerError, 'reconciliation_required'):
            self.process(retry_failed=True)

    def test_final_ledger_write_failure_preserves_pending(self):
        original = trigger.write_ledger
        def fail_final(path, value):
            if value['deliveries']['fixture-delivery-1']['state'] == 'succeeded':
                raise OSError('synthetic-disk-failure')
            original(path, value)
        with patch.object(trigger, 'write_ledger', side_effect=fail_final):
            with self.assertRaises(OSError):
                self.process()
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.ledger()['deliveries']['fixture-delivery-1']['state'], 'pending')
        with self.assertRaisesRegex(trigger.TriggerError, 'reconciliation_required'):
            self.process(retry_failed=True)

    def test_concurrent_invocations_do_not_both_refresh(self):
        entered, release = threading.Event(), threading.Event()
        def blocked(*args):
            self.refresh(*args)
            entered.set()
            self.assertTrue(release.wait(5))
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.process, refresh=blocked)
            self.assertTrue(entered.wait(5))
            try:
                with self.assertRaisesRegex(trigger.TriggerError, 'busy_or_reconciliation_required'):
                    self.process()
            finally:
                release.set()
            self.assertEqual(future.result()['status'], 'succeeded')
        self.assertEqual(len(self.calls), 1)

    def test_manual_refresh_blocks_event_then_explicit_retry_succeeds(self):
        entered, release = threading.Event(), threading.Event()
        calls = []
        def collect(config, api=None):
            calls.append(True)
            if len(calls) == 1:
                entered.set()
                self.assertTrue(release.wait(5))
            return fixtures.snapshot(config)
        with patch.object(trigger.router, 'collect', side_effect=collect):
            with ThreadPoolExecutor(max_workers=1) as pool:
                manual = pool.submit(trigger.router.refresh, self.config,
                                     self.args['snapshot'], self.args['status'])
                self.assertTrue(entered.wait(5))
                try:
                    with self.assertRaisesRegex(trigger.TriggerError, '^refresh_failed$'):
                        self.process(refresh=trigger.router.refresh)
                    record = self.ledger()['deliveries']['fixture-delivery-1']
                    self.assertEqual(record['state'], 'failed')
                    self.assertEqual(len(calls), 1)
                finally:
                    release.set()
                manual.result()
            self.assertEqual(self.process(refresh=trigger.router.refresh, retry_failed=True)['status'], 'succeeded')
        self.assertEqual(len(calls), 2)

    def test_event_refresh_blocks_manual_refresh(self):
        entered, release = threading.Event(), threading.Event()
        def collect(config, api=None):
            entered.set()
            self.assertTrue(release.wait(5))
            return fixtures.snapshot(config)
        with patch.object(trigger.router, 'collect', side_effect=collect) as mock_collect:
            with ThreadPoolExecutor(max_workers=1) as pool:
                event = pool.submit(self.process, refresh=trigger.router.refresh)
                self.assertTrue(entered.wait(5))
                try:
                    with self.assertRaisesRegex(trigger.router.RoutingError, 'refresh_busy_or_reconciliation_required'):
                        trigger.router.refresh(self.config, self.args['snapshot'], self.args['status'])
                    self.assertEqual(mock_collect.call_count, 1)
                finally:
                    release.set()
                self.assertEqual(event.result()['status'], 'succeeded')

    def test_stale_lock_and_corrupt_ledger_fail_closed(self):
        lock = Path(str(self.args['ledger']) + '.lock')
        lock.mkdir()
        with self.assertRaisesRegex(trigger.TriggerError, 'busy_or_reconciliation_required'):
            self.process()
        self.assertTrue(lock.exists())
        lock.rmdir()
        self.args['ledger'].write_text('{}')
        with self.assertRaisesRegex(trigger.TriggerError, 'ledger_invalid_or_binding_changed'):
            self.process()
        self.assertEqual(self.calls, [])

    def test_distinct_paths_and_hardlink_alias(self):
        before = self.args['policy'].read_bytes()
        for output in ('snapshot', 'status', 'ledger'):
            with self.subTest(output=output):
                with self.assertRaisesRegex(trigger.TriggerError, 'path_collision'):
                    self.process(**{output: self.args['policy']})
        alias = self.root / 'alias.json'
        os.link(self.args['policy'], alias)
        with self.assertRaisesRegex(trigger.TriggerError, 'path_collision'):
            self.process(snapshot=alias)
        self.assertEqual(before, self.args['policy'].read_bytes())

    def test_ledger_policy_binding(self):
        self.process()
        self.config['freshness']['proposed_max_age_seconds'] += 1
        self.args['policy'].write_text(json.dumps(self.config))
        with self.assertRaisesRegex(trigger.TriggerError, 'ledger_invalid_or_binding_changed'):
            self.process(delivery='new-delivery')

    def test_cli_errors_are_sanitized(self):
        args = self.args | {'signature': 'sha256=' + '0' * 64}
        command = [sys.executable, str(ROOT / 'automation/refresh_trigger.py')]
        for key, value in args.items():
            command.extend(['--' + key, str(value)])
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout), {'status': 'signature_invalid'})
        self.assertEqual(result.stderr, '')
        self.assertNotIn(self.secret, result.stdout)

    def test_cli_process_respects_existing_lock(self):
        Path(str(self.args['ledger']) + '.lock').mkdir()
        command = [sys.executable, str(ROOT / 'automation/refresh_trigger.py')]
        for key, value in self.args.items():
            command.extend(['--' + key, str(value)])
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout), {'status': 'busy_or_reconciliation_required'})
        self.assertFalse(self.args['ledger'].exists())


if __name__ == '__main__':
    unittest.main()
