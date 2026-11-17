import assert from 'node:assert/strict'
import test from 'node:test'
import { REQUIRED, validateIdentity, validatePermissions, safeErrorMessage } from '../automation/collector_token.mjs'

test('requires exact read-only permissions; rejects old writing App and extra reads', () => {
  validatePermissions({ ...REQUIRED })
  for (const bad of [{ members: 'write' }, { ...REQUIRED, members: 'write' }, { ...REQUIRED, contents: 'read' }, {}]) {
    assert.throws(() => validatePermissions(bad))
  }
})
test('binds App, installation, organization and complete scope', () => {
  const app = { id: 7, permissions: REQUIRED, events: [] }
  const installation = { app_id: 7, account: { id: 8, type: 'Organization' }, permissions: REQUIRED, repository_selection: 'all', suspended_at: null }
  validateIdentity(app, installation, 7, 8)
  for (const change of [{ app_id: 9 }, { account: { id: 9, type: 'Organization' } }, { repository_selection: 'selected' }, { suspended_at: 'now' }]) {
    assert.throws(() => validateIdentity(app, { ...installation, ...change }, 7, 8))
  }
  assert.throws(() => validateIdentity({ ...app, events: ['membership'] }, installation, 7, 8))
})

test('reported collector errors retain only allowlisted diagnostics', () => {
  assert.match(safeErrorMessage(new Error('Collector installation is missing a policy repository')), /missing a policy repository/)
  assert.match(safeErrorMessage(new Error('Collector authentication endpoint failed (HTTP 403)')), /HTTP 403/)
  assert.doesNotMatch(safeErrorMessage(new Error('SYNTHETIC_SECRET from untrusted exception')), /SYNTHETIC_SECRET/)
})
