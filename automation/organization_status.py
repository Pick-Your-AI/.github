"""Durable public-safe run receipt; never serialize raw collector responses."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value if parsed.tzinfo is not None else None
    except ValueError:
        return None


def finish(receipt, private_status, outcome):
    result = dict(receipt)
    result['finished_at'] = now()
    result['publication_step'] = outcome if outcome in {'success', 'failure', 'cancelled', 'skipped'} else 'unknown'
    status = private_status.get('status')
    result['collection_status'] = status if status in {'complete', 'failed'} else 'not_recorded'
    result['collection_observed_at'] = timestamp(private_status.get('observed_at')) if status == 'complete' else None
    value = private_status.get('content_sha256')
    result['public_content_sha256'] = value if isinstance(value, str) and re.fullmatch(r'[a-f0-9]{64}', value) else None
    result['changed'] = private_status.get('changed') if type(private_status.get('changed')) is bool else None
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('start', 'finish'))
    parser.add_argument('--outcome', default='unknown')
    args = parser.parse_args()
    output = Path(os.environ['PYA_RUN_STATUS'])
    if args.operation == 'start':
        public = json.loads(Path('docs/organization/current/organization.json').read_text(encoding='utf-8'))
        receipt = {
            'schema_version': 1, 'started_at': now(), 'finished_at': None,
            'run_id': os.environ.get('GITHUB_RUN_ID'), 'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
            'event': os.environ.get('GITHUB_EVENT_NAME'), 'workflow_revision': os.environ.get('GITHUB_SHA'),
            'last_merged_observation_at': timestamp(public.get('observation', {}).get('completed_at')),
            'collection_status': 'not_recorded', 'collection_observed_at': None,
            'publication_step': 'not_started', 'public_content_sha256': None, 'changed': None,
        }
    else:
        receipt = json.loads(output.read_text(encoding='utf-8'))
        private_path = Path(os.environ['PYA_STATE']) / 'status.json'
        private_status = json.loads(private_path.read_text(encoding='utf-8')) if private_path.exists() else {}
        receipt = finish(receipt, private_status, args.outcome)
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a', encoding='utf-8') as summary:
            summary.write('## Public-safe refresh receipt\n\n```json\n' + json.dumps(receipt, indent=2) + '\n```\n')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
