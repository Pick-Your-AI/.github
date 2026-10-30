// Runs only in the protected organization-collector environment. No key files.
import { createPrivateKey, sign } from 'node:crypto'
import { appendFileSync, readFileSync } from 'node:fs'
import { pathToFileURL } from 'node:url'

export const REQUIRED = Object.freeze({
  metadata: 'read', administration: 'read', members: 'read', organization_projects: 'read',
})

export function validatePermissions(actual) {
  if (!actual || JSON.stringify(Object.entries(actual).sort()) !== JSON.stringify(Object.entries(REQUIRED).sort())) {
    throw new Error('Collector permissions must exactly match the approved read-only permission set')
  }
}

export function validateIdentity(app, installation, appId, orgId) {
  if (!Number.isSafeInteger(appId) || app.id !== appId || installation.app_id !== appId ||
      installation.account?.id !== orgId || installation.account?.type !== 'Organization' ||
      installation.suspended_at || installation.repository_selection !== 'all') {
    throw new Error('Collector App identity, organization, scope or installation status does not match')
  }
  validatePermissions(app.permissions)
  validatePermissions(installation.permissions)
  if (!Array.isArray(app.events) || app.events.length) throw new Error('Collector must not subscribe to write/event automation')
}

async function main() {
  const appId = Number(process.env.APP_ID)
  const policy = JSON.parse(readFileSync('governance/escalation-policy.json', 'utf8'))
  const now = Math.floor(Date.now() / 1000)
  const encode = value => Buffer.from(JSON.stringify(value)).toString('base64url')
  const unsigned = `${encode({ alg: 'RS256', typ: 'JWT' })}.${encode({ iat: now - 60, exp: now + 540, iss: String(appId) })}`
  const signature = sign('RSA-SHA256', Buffer.from(unsigned), createPrivateKey(process.env.APP_KEY)).toString('base64url')
  const jwt = `${unsigned}.${signature}`
  async function api(path, token, method = 'GET', body) {
    const response = await fetch(`https://api.github.com${path}`, {
      method, redirect: 'error', signal: AbortSignal.timeout(30000),
      headers: { Accept: 'application/vnd.github+json', 'Content-Type': 'application/json', Authorization: `Bearer ${token}`, 'X-GitHub-Api-Version': '2022-11-28' },
      body: body ? JSON.stringify(body) : undefined,
    })
    if (!response.ok) throw new Error(`Collector authentication endpoint failed (HTTP ${response.status})`)
    return response.status === 204 ? null : response.json()
  }
  const app = await api('/app', jwt)
  const installation = await api(`/orgs/${encodeURIComponent(policy.organization.login)}/installation`, jwt)
  validateIdentity(app, installation, appId, policy.organization.id)
  const minted = await api(`/app/installations/${installation.id}/access_tokens`, jwt, 'POST', { permissions: REQUIRED })
  if (typeof minted.token !== 'string' || !minted.token || /[\r\n]/.test(minted.token)) throw new Error('Invalid collector token response')
  // Mask before any validation that could fail; never print API payloads.
  console.log(`::add-mask::${minted.token}`)
  try {
    validatePermissions(minted.permissions)
    const ids = new Set()
    for (let page = 1; ; page++) {
      if (page > 10000) throw new Error('Collector repository pagination did not terminate')
      const response = await api(`/installation/repositories?per_page=100&page=${page}`, minted.token)
      if (!Array.isArray(response.repositories)) throw new Error('Collector repository response is incomplete')
      for (const repo of response.repositories) {
        if (ids.has(repo.id)) throw new Error('Collector repository pagination repeated an identity')
        ids.add(repo.id)
      }
      if (ids.size === response.total_count) break
      if (!response.repositories.length || ids.size > response.total_count) throw new Error('Collector repository pagination is incomplete')
    }
    if (policy.repositories.some(repo => !ids.has(repo.id))) throw new Error('Collector installation is missing a policy repository')
    appendFileSync(process.env.GITHUB_OUTPUT, `token=${minted.token}\ninstallation-id=${installation.id}\n`)
    appendFileSync(process.env.GITHUB_STEP_SUMMARY,
      `## Collector credential verification\n\nApp ${app.id}; installation ${installation.id}; expected organization and all policy repositories verified; exact read-only permissions verified. API payloads withheld. Endpoint collection coverage is verified separately.\n`)
  } catch (error) {
    await api('/installation/token', minted.token, 'DELETE').catch(() => {})
    throw error
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(() => { console.error('Collector credential verification failed; no restricted payload is logged.'); process.exitCode = 1 })
}
