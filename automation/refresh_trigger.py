"""Prepared, inactive adapter for an externally authorized webhook receiver.

No HTTP server, subscription, schedule or receiver is installed. The receiver
must retain the original body bytes and pass trusted GitHub event/delivery headers.
PYA_WEBHOOK_SECRET supplies the HMAC secret; existing router credentials remain
in its environment. Nothing here changes memberships, permissions or policy.

Supported GitHub events (https://docs.github.com/en/webhooks/webhook-events-and-payloads):
membership: added, removed; team: created, deleted, edited, added_to_repository,
removed_from_repository; team_add: no action field. Other events fail closed.

Use one private ledger for the configured policy/snapshot/status. Failed delivery
retries require --retry-failed, at most three total attempts. Pending records or
leftover lock directories require operator reconciliation with router status and
snapshot; never automatically erase them or replay an uncertain attempt. The
operator must stop all invocations before repairing private state. A successful
refresh with an uncommitted ledger may be repeated only after that reconciliation.
The adapter locks its delivery ledger; router.refresh owns the shared snapshot
lock for both manual and event refreshes. Snapshot contention records a failed
delivery and requires an explicit retry after the active refresh completes.
This is a fixture-tested interface, not proof of live GitHub delivery.
"""
import argparse
from contextlib import contextmanager
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile


SPEC = importlib.util.spec_from_file_location('governance_router', Path(__file__).resolve().parents[1] / 'governance' / 'router.py')
router = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(router)
SUPPORTED = {'membership': {'added', 'removed'},
             'team': {'created', 'deleted', 'edited', 'added_to_repository', 'removed_from_repository'},
             'team_add': {None}}
MAX_ATTEMPTS = 3


class TriggerError(Exception):
    """Message is a fixed, safe status code, never external input."""


def sync_directory(path):
    if os.name == 'posix':
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def write_ledger(path, value):
    fd, temporary = tempfile.mkstemp(prefix='.delivery-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def locked(path):
    # mkdir is exclusive across processes on local filesystems. Never infer that
    # an existing lock is stale from a PID, timestamp, or elapsed duration.
    try:
        path.mkdir(mode=0o700)
    except FileExistsError:
        raise TriggerError('busy_or_reconciliation_required') from None
    try:
        sync_directory(path.parent)
        yield
    finally:
        path.rmdir()
        sync_directory(path.parent)


def distinct(paths):
    for i, path in enumerate(paths):
        for other in paths[:i]:
            if path == other or path in other.parents or other in path.parents:
                raise TriggerError('path_collision')
            if path.exists() and other.exists() and os.path.samefile(path, other):
                raise TriggerError('path_collision')


def process(*, payload, event, delivery, signature, policy, snapshot, status, ledger,
            retry_failed=False, refresh=None):
    paths = [Path(p).resolve() for p in (payload, policy, snapshot, status, ledger)]
    payload_path, policy_path, snapshot_path, status_path, ledger_path = paths
    locks = [Path(str(ledger_path) + '.lock'), Path(str(snapshot_path) + '.refresh.lock')]
    distinct(paths + locks)
    secret = os.environ.get('PYA_WEBHOOK_SECRET', '')
    if not secret:
        raise TriggerError('secret_missing')
    if not isinstance(signature, str) or not re.fullmatch(r'sha256=[0-9a-f]{64}', signature):
        raise TriggerError('signature_invalid')
    if not re.fullmatch(r'[A-Za-z0-9-]{1,128}', delivery):
        raise TriggerError('delivery_invalid')
    with payload_path.open('rb') as stream:
        body = stream.read(2 * 1024 * 1024 + 1)
    if len(body) > 2 * 1024 * 1024:
        raise TriggerError('payload_too_large')
    expected = 'sha256=' + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise TriggerError('signature_invalid')
    try:
        value = json.loads(body)
        if not isinstance(value, dict) or event not in SUPPORTED or value.get('action') not in SUPPORTED[event]:
            raise TriggerError('event_unsupported')
        if event == 'team_add' and 'action' in value:
            raise TriggerError('event_unsupported')
        organization_id = value.get('organization', {}).get('id')
        if type(organization_id) is not int or organization_id <= 0:
            raise TriggerError('organization_invalid')
    except (ValueError, AttributeError, TypeError):
        raise TriggerError('payload_invalid') from None
    config = router.validate_policy(router.read_json(policy_path))
    if organization_id != config['organization']['id']:
        raise TriggerError('organization_mismatch')
    binding = {'policy_sha256': router.digest(config), 'snapshot': str(snapshot_path), 'status': str(status_path)}
    fingerprint = hashlib.sha256(event.encode() + b'\0' + body).hexdigest()
    for target in (ledger_path, snapshot_path, status_path):
        target.parent.mkdir(parents=True, exist_ok=True)
    # Never acquire the snapshot lock here: router.refresh acquires that same
    # lock for all callers, including the manual CLI, without a bypass flag.
    with locked(locks[0]):
        state = router.read_json(ledger_path) if ledger_path.exists() else {
            'schema_version': 1, 'binding': binding, 'deliveries': {}}
        if (not isinstance(state, dict) or state.get('schema_version') != 1 or
                state.get('binding') != binding or not isinstance(state.get('deliveries'), dict)):
            raise TriggerError('ledger_invalid_or_binding_changed')
        previous = state['deliveries'].get(delivery)
        attempts = 0
        if previous is not None:
            if not isinstance(previous, dict) or previous.get('fingerprint') != fingerprint:
                raise TriggerError('delivery_conflict')
            if previous.get('state') == 'succeeded':
                return {'status': 'duplicate_succeeded'}
            if previous.get('state') == 'pending':
                raise TriggerError('reconciliation_required')
            attempts = previous.get('attempts')
            if previous.get('state') != 'failed' or type(attempts) is not int or not 1 <= attempts <= MAX_ATTEMPTS:
                raise TriggerError('ledger_invalid')
            if not retry_failed:
                raise TriggerError('retry_requires_explicit_flag')
            if attempts >= MAX_ATTEMPTS:
                raise TriggerError('retry_exhausted')
        record = {'fingerprint': fingerprint, 'state': 'pending', 'attempts': attempts + 1}
        state['deliveries'][delivery] = record
        write_ledger(ledger_path, state)
        try:
            (refresh or router.refresh)(config, snapshot_path, status_path)
        except Exception:
            record['state'] = 'failed'
            write_ledger(ledger_path, state)
            raise TriggerError('refresh_failed') from None
        record['state'] = 'succeeded'
        write_ledger(ledger_path, state)
    return {'status': 'succeeded'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('payload', 'event', 'delivery', 'signature', 'policy', 'snapshot', 'status', 'ledger'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--retry-failed', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = process(**vars(args))
    except TriggerError as error:
        result = {'status': str(error)}
    except Exception:
        # Never print paths, raw API errors, payloads, signatures, or credentials.
        result = {'status': 'local_or_configuration_failure'}
    print(json.dumps(result, sort_keys=True))
    return 0 if result['status'] in ('succeeded', 'duplicate_succeeded') else 1


if __name__ == '__main__':
    raise SystemExit(main())
