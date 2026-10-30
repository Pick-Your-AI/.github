# Routing refresh activation checklist

Nothing in this directory installs a receiver or recurring job. The executable collector works manually; `routing-directory.yml.example` is an inactive preview workflow. The separate `refresh_trigger.py` adapter accepts authenticated event files from a future approved receiver. Fixture tests are not evidence of a real GitHub delivery.

## Event adapter

An approved receiver must preserve exact request bytes, verify transport/source expectations, and pass the GitHub event, delivery and signature headers. The adapter verifies HMAC-SHA256 again with `PYA_WEBHOOK_SECRET` from its environment, validates organization identity, and accepts only its documented membership/team actions. It does not start an HTTP listener or create a webhook.

```sh
python automation/refresh_trigger.py --payload /private/path/body.json \
  --event "$EVENT_NAME" --delivery "$DELIVERY_ID" --signature "$SIGNATURE" \
  --policy governance/escalation-policy.json \
  --snapshot /private/path/routing-snapshot.json \
  --status /private/path/routing-status.json \
  --ledger /private/path/delivery-ledger.json
```

Keep payloads, ledgers, credentials and snapshots private. The ledger binds to the policy/output paths, rejects conflicting replay, and suppresses already successful deliveries. Failed attempts require explicit `--retry-failed`, with a maximum of three attempts. Pending attempts and surviving locks require an operator to reconcile the last successful snapshot and ledger; never delete them merely because a timeout expired. No event sends an escalation message or changes GitHub configuration.

## Periodic reconciliation proposal

The fallback is the same read-only `router.py refresh` command. A proposed maximum interval is one day; the owner must approve the interval, cache threshold, credential and destination before a scheduler is configured. The checked-in preview workflow has only manual dispatch and remains outside `.github/workflows/`. Adding an approved schedule and moving it to that directory is a separate reviewable activation change. Its first scheduled run and failure behavior must be read back before claiming the fallback operational.

A future activation must specify durable retention for the last-good private snapshot and failure status. An ephemeral Actions runner alone is not that retention mechanism. Publish only the sanitized directory, skip unchanged output, retain exact source/tool revisions and timestamps, and fail visibly when organization data is inaccessible. Do not use the membership-writing Early Contributors credential by default.

## Required activation evidence

- Owner-approved read-only credential scopes, receiver/publication destination and thresholds.
- A real supported GitHub event delivery, authenticated acceptance, collection receipt and public-output readback.
- A real scheduled fallback run, unchanged-output behavior and API-failure recovery retaining the prior verification time.
- Fresh agent and contributor flows against merged entrypoints, with local-template overrides verified.

The current PR provides source, fixture validation and manual readback; installation, scheduling, merged-template rendering and ongoing operation remain separate acceptance items under #17.

## Current chart activation extension

The [organization operation guide](../docs/ORGANIZATION.md) now prepares one shared chart/directory collector and protected artifact publisher. Its proposed hourly reconciliation supersedes the earlier daily fallback suggestion above for organization charts. The earlier workflow example and event adapter remain inactive reference material. The new workflow still requires the dedicated read-only credential, independent merge review and verified real operation; no activation is claimed by this documentation.
