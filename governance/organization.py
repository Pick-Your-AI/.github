"""Organization inventory and public projection; policy remains in router.py.

Only fixed read queries are sent to GitHub. Raw responses and rosters never enter
the public model. Failure to collect any required inventory aborts publication.
"""
from __future__ import annotations

import argparse
import copy
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

try:
    from . import router
except ImportError:
    import router

PROJECTS = """query InventoryProjects($org:String!, $cursor:String) {
 organization(login:$org) { id projectsV2(first:100,after:$cursor) {
 nodes { id number title url public closed } pageInfo { hasNextPage endCursor }
 } } }"""
PROJECT_REPOS = """query InventoryProjectRepositories($id:ID!, $cursor:String) {
 node(id:$id) { ... on ProjectV2 { id repositories(first:100,after:$cursor) {
 nodes { databaseId } pageInfo { hasNextPage endCursor }
 } } } }"""


def connection(api, query, variables, extract, identity):
    records, seen, cursors = [], set(), set()
    cursor = None
    while True:
        args = ['graphql', '--method', 'POST', '-f', 'query=' + query]
        args += [part for key, val in variables.items() for part in ('-f', f'{key}={val}')]
        if cursor:
            args += ['-f', 'cursor=' + cursor]
        try:
            page = extract(api._call(args, 'organization-inventory'))
            nodes, info = page['nodes'], page['pageInfo']
            if not isinstance(nodes, list) or type(info['hasNextPage']) is not bool:
                raise ValueError()
            for node in nodes:
                key = node[identity]
                if key is None or key in seen:
                    raise ValueError()
                seen.add(key)
                records.append(node)
            if not info['hasNextPage']:
                break
            cursor = info['endCursor']
            if not cursor or cursor in cursors or len(cursors) >= 10000:
                raise ValueError()
            cursors.add(cursor)
        except router.RoutingError:
            raise
        except (KeyError, TypeError, ValueError):
            raise router.RoutingError('Incomplete or invalid Project connection') from None
    api.coverage.append({'resource': 'projects' if query == PROJECTS else 'project-repositories',
                         'status': 'complete', 'pages': len(cursors) + 1})
    return records


def validate_mapping(mapping, policy):
    router.object_keys(mapping, ('schema_version', 'owner', 'decision_refs', 'approved_public', 'areas', 'project_responsibilities'), 'mapping')
    if mapping['schema_version'] != 1:
        raise router.RoutingError('Unsupported mapping version')
    router.string(mapping['owner'], 'mapping.owner')
    router.refs(mapping['decision_refs'], 'mapping.refs', True)
    router.object_keys(mapping['approved_public'], ('teams', 'repositories', 'projects'), 'approved_public')
    for kind in ('teams', 'repositories'):
        router.ids(mapping['approved_public'][kind], kind)
    projects = mapping['approved_public']['projects']
    if not isinstance(projects, list) or len(set(projects)) != len(projects):
        raise router.RoutingError('Duplicate Project approvals')
    for value in projects:
        router.string(value, 'project ID')
    seen_projects = set()
    for role in mapping['project_responsibilities']:
        router.object_keys(role, ('project_id', 'state', 'team_ids', 'decision_refs'), 'Project responsibility')
        if role['project_id'] not in projects or role['project_id'] in seen_projects:
            raise router.RoutingError('Invalid or duplicate Project responsibility')
        seen_projects.add(role['project_id'])
        router.enum(role['state'], {'accepted', 'unresolved'}, 'Project responsibility state')
        router.ids(role['team_ids'], 'Project responsibility teams')
        router.refs(role['decision_refs'], 'Project responsibility provenance', role['state'] == 'accepted')
        if bool(role['team_ids']) != (role['state'] == 'accepted') or not set(role['team_ids']) <= set(mapping['approved_public']['teams']):
            raise router.RoutingError('Project responsibility requires approved teams or explicit unresolved state')
    seen = set()
    for area in mapping['areas']:
        router.object_keys(area, ('id', 'name', 'teams', 'repositories', 'projects', 'decision_refs'), 'area')
        if not re.fullmatch('[a-z0-9-]+', area['id']) or area['id'] in seen:
            raise router.RoutingError('Invalid or duplicate area')
        seen.add(area['id'])
        router.string(area['name'], 'area.name')
        router.refs(area['decision_refs'], 'area.refs', True)
        for kind in ('teams', 'repositories'):
            router.ids(area[kind], kind)
        if not isinstance(area['projects'], list) or len(set(area['projects'])) != len(area['projects']):
            raise router.RoutingError('Invalid area Project IDs')
        for kind in ('teams', 'repositories', 'projects'):
            if not set(area[kind]) <= set(mapping['approved_public'][kind]):
                raise router.RoutingError('Area refers to unapproved entity')
    router.validate_policy(policy)


def collect(policy, mapping, source_revision, api=None):
    validate_mapping(mapping, policy)
    api = api or router.GitHub()
    started = router.now()
    org = api.get('orgs/' + policy['organization']['login'])
    if org['id'] != policy['organization']['id']:
        raise router.RoutingError('Organization identity mismatch')
    teams = []
    for row in api.pages(f"orgs/{org['login']}/teams"):
        teams.append({'id': row['id'], 'node_id': row['node_id'], 'name': row['name'],
                      'slug': row['slug'], 'privacy': row['privacy'],
                      'parent_id': (row.get('parent') or {}).get('id'),
                      'members': api.members(row, 'IMMEDIATE'),
                      'inherited_members': api.members(row, 'CHILD_TEAM')})
    repositories = []
    for row in api.pages(f"orgs/{org['login']}/repos"):
        # Unknown access is fatal; a successful empty list is authoritative only
        # for the authenticated identity's visible inventory.
        grants = api.pages(f"repos/{row['full_name']}/teams")
        repositories.append({'id': row['id'], 'node_id': row['node_id'], 'name': row['name'],
                             'full_name': row['full_name'], 'private': row['private'],
                             'visibility': row['visibility'], 'archived': row['archived'],
                             'team_grants': sorted([{'team_id': g['id'], 'permission': g['permission']} for g in grants], key=lambda g: g['team_id'])})
    projects = connection(api, PROJECTS, {'org': org['login']},
                          lambda r: r['data']['organization']['projectsV2'], 'id')
    for project in projects:
        project['repository_ids'] = sorted(row['databaseId'] for row in connection(
            api, PROJECT_REPOS, {'id': project['id']},
            lambda r: r['data']['node']['repositories'], 'databaseId'))
    # The existing resolver consumes exactly this transaction's routing snapshot.
    routing = router.collect(policy, api)
    # A changing org during collection must not produce two competing snapshots.
    all_teams = {t['id']: t for t in teams}
    for t in routing['teams']:
        if t['status'] != 'available' or t['id'] not in all_teams:
            raise router.RoutingError('Routing team unavailable in inventory')
        observed = all_teams[t['id']]
        if any(observed[k] != t[k] for k in ('name', 'slug', 'parent_id', 'privacy')) or observed['members'] != t['direct_members'] or observed['inherited_members'] != t['inherited_members']:
            raise router.RoutingError('Organization changed during collection; retry')
    all_repos = {r['id']: r for r in repositories}
    for r in routing['repositories']:
        observed = all_repos.get(r['id'])
        if observed is None or any(observed[k] != r[k] for k in ('full_name', 'private', 'team_grants')):
            raise router.RoutingError('Repository changed during collection; retry')
    result = {'schema_version': 1, 'organization': {'id': org['id'], 'login': org['login'], 'node_id': org['node_id']},
              'teams': sorted(teams, key=lambda r: r['id']),
              'repositories': sorted(repositories, key=lambda r: r['id']),
              'projects': sorted(projects, key=lambda r: r['id']), 'routing': routing,
              'observation': {'started_at': started, 'completed_at': router.now(),
                              'source_revision': source_revision, 'policy_revision': router.digest(policy),
                              'mapping_revision': router.digest(mapping), 'source': 'api.github.com',
                              'scope': 'entities visible to authenticated collector; hidden entities are unknown',
                              'coverage': api.coverage}}
    validate_model(result, policy, mapping)
    return result


def validate_model(model, policy, mapping):
    validate_mapping(mapping, policy)
    if model['schema_version'] != 1 or model['organization']['id'] != policy['organization']['id']:
        raise router.RoutingError('Invalid model identity/version')
    if model['observation']['policy_revision'] != router.digest(policy):
        raise router.RoutingError('Model policy mismatch')
    router.login(model['organization']['login'], 'organization login')
    router.timestamp(model['observation']['completed_at'])
    if any(c['status'] != 'complete' for c in model['observation']['coverage']):
        raise router.RoutingError('Incomplete collection')
    for kind in ('teams', 'repositories', 'projects'):
        rows = model[kind]
        if len({r['id'] for r in rows}) != len(rows):
            raise router.RoutingError('Duplicate identity')
    teams = {t['id']: t for t in model['teams']}
    for t in teams.values():
        router.positive(t['id'], 'team ID')
        router.string(t['name'], 'team name')
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', t['slug']):
            raise router.RoutingError('Invalid team slug')
        router.enum(t['privacy'], {'closed', 'secret'}, 'privacy')
        current, seen = t, set()
        while current['parent_id'] is not None:
            if current['id'] in seen or current['parent_id'] not in teams:
                raise router.RoutingError('Cyclic or missing team parent')
            seen.add(current['id'])
            current = teams[current['parent_id']]
    router.validate_snapshot(policy, model['routing'])
    for r in model['repositories']:
        if not re.fullmatch(re.escape(model['organization']['login']) + r'/[A-Za-z0-9_.-]+', r['full_name']):
            raise router.RoutingError('Invalid repository name or transferred repository')
        if type(r['private']) is not bool or type(r['archived']) is not bool:
            raise router.RoutingError('Invalid repository visibility/archive state')
    for p in model['projects']:
        router.string(p['id'], 'Project node ID')
        router.positive(p['number'], 'Project number')
        if type(p['public']) is not bool or type(p['closed']) is not bool:
            raise router.RoutingError('Invalid Project state')


def public_model(model, policy, mapping):
    validate_model(model, policy, mapping)
    approval = mapping['approved_public']
    teams = [{'id': t['id'], 'name': t['name'], 'url': f"https://github.com/orgs/{model['organization']['login']}/teams/{t['slug']}",
              'parent_id': t['parent_id']} for t in model['teams'] if t['id'] in approval['teams'] and t['privacy'] == 'closed']
    repositories = [{'id': r['id'], 'name': r['full_name'], 'url': f"https://github.com/{r['full_name']}",
                     'archived': r['archived']} for r in model['repositories'] if r['id'] in approval['repositories'] and not r['private']]
    projects = [{'id': p['id'], 'name': p['title'], 'url': f"https://github.com/orgs/{model['organization']['login']}/projects/{p['number']}",
                 'closed': p['closed']} for p in model['projects'] if p['id'] in approval['projects'] and p['public']]
    allowed = {kind: {r['id'] for r in rows} for kind, rows in [('teams', teams), ('repositories', repositories), ('projects', projects)]}
    for t in teams:
        if t['parent_id'] not in allowed['teams']:
            t['parent_id'] = None
    areas = [{**a, **{kind: [x for x in a[kind] if x in allowed[kind]] for kind in allowed}} for a in mapping['areas']]
    edges = []
    for t in teams:
        if t['parent_id'] is not None:
            edges.append({'kind': 'github_parent', 'from': f"team:{t['parent_id']}", 'to': f"team:{t['id']}"})
    for r in model['repositories']:
        if r['id'] in allowed['repositories']:
            for grant in r['team_grants']:
                if grant['team_id'] in allowed['teams']:
                    edges.append({'kind': 'access', 'from': f"team:{grant['team_id']}", 'to': f"repository:{r['id']}", 'label': grant['permission']})
    for p in model['projects']:
        if p['id'] in allowed['projects']:
            for rid in p['repository_ids']:
                if rid in allowed['repositories']:
                    edges.append({'kind': 'project_link', 'from': f"project:{p['id']}", 'to': f'repository:{rid}'})
    roles = []
    project_roles = []
    configured_projects = {r['project_id']: r for r in mapping['project_responsibilities']}
    for project in projects:
        role = configured_projects.get(project['id'], {'project_id': project['id'], 'state': 'unresolved', 'team_ids': [], 'decision_refs': []})
        role = {**role, 'team_ids': [t for t in role['team_ids'] if t in allowed['teams']]}
        if role['state'] == 'accepted' and not role['team_ids']:
            role['state'] = 'unavailable'
        project_roles.append(role)
        if role['state'] == 'accepted':
            for tid in role['team_ids']:
                edges.append({'kind': 'project_responsibility', 'from': f'team:{tid}', 'to': f"project:{project['id']}"})
    for r in policy['repositories']:
        if r['id'] not in allowed['repositories']:
            continue
        for role in r['roles']:
            roles.append({'repository_id': r['id'], 'level': role['level'], 'state': role['state'],
                          'team_ids': [x for x in role['team_ids'] if x in allowed['teams']],
                          'decision_refs': role['decision_refs']})
            if role['state'] == 'accepted':
                for tid in role['team_ids']:
                    if tid in allowed['teams']:
                        edges.append({'kind': 'responsibility', 'from': f'team:{tid}', 'to': f"repository:{r['id']}", 'label': role['level']})
    routing = router.directory(policy, model['routing'], live=True)
    configured_ids = {r['full_name']: r['id'] for r in policy['repositories']}
    observed_repositories = {r['id']: r for r in repositories}
    for r in routing['repositories']:
        observed = observed_repositories.get(configured_ids[r['repository']])
        if observed:
            r['repository'] = observed['name']
            r['url'] = observed['url']
    # Keep only the already approved destinations, not every closed team.
    allowed_urls = {t['url'] for t in teams}
    routing['repositories'] = [r for r in routing['repositories'] if r['url'] in {x['url'] for x in repositories}]
    for r in routing['repositories']:
        for level in r['levels']:
            if any(t['url'] not in allowed_urls for t in level['teams']):
                level['disposition'] = 'unapproved_destination_withheld'
            level['teams'] = [t for t in level['teams'] if t['url'] in allowed_urls]
    routing['coordination_roles'] = [r for r in routing['coordination_roles'] if r['team_url'] in allowed_urls]
    mapped = {kind: {x for a in areas for x in a[kind]} for kind in allowed}
    return {'schema_version': 1, 'organization': model['organization'], 'teams': teams, 'repositories': repositories,
            'projects': projects, 'areas': areas, 'roles': roles, 'project_roles': project_roles, 'routing': routing, 'relationships': sorted(edges, key=router.canonical),
            'unavailable_approved': {kind: sorted(set(approval[kind]) - allowed[kind], key=str) for kind in allowed},
            'unmapped': {kind: sorted(allowed[kind] - mapped[kind], key=str) for kind in allowed},
            'observation': {**{k: model['observation'][k] for k in ('completed_at', 'source_revision', 'policy_revision', 'scope')},
                            'mapping_revision': router.digest(mapping)},
            'coverage': {'inventory': 'complete for collector-visible data', 'public': 'approved entities only; excluded and inaccessible identities undisclosed',
                         'hierarchy': 'induced hierarchy of approved teams; omitted parents are not roots of the internal hierarchy'},
            'freshness_threshold_seconds': 10800, 'freshness_basis': 'proposed operational setting: three hourly intervals'}


def semantic(value):
    result = copy.deepcopy(value)
    result.pop('observation', None)
    result.get('routing', {}).pop('snapshot_content_verified_at', None)
    return router.digest(result)


def node_id(value):
    return 'n' + router.digest(value)[:20]


def label(value):
    # HTML-free Mermaid text labels preserve Unicode directly. Entity escapes
    # would render literally with htmlLabels=false. Replace grammar delimiters
    # with visible code points, never markup or executable Mermaid directives.
    forbidden = '"\\<>[]{}|%#;`'
    return ''.join(c if ord(c) >= 32 and c not in forbidden else f' U+{ord(c):04X} ' for c in value)[:1200]


def charts(public):
    nodes = {f'{kind}:{r["id"]}': r for kind, plural in [('team', 'teams'), ('repository', 'repositories'), ('project', 'projects')] for r in public[plural]}
    def chart(keys, edge_kinds):
        lines = ['flowchart TB', 'accTitle: Pick Your AI organization relationships',
                 'accDescr: Solid arrows show actual team parents. Dotted labeled arrows distinguish responsibility and Project links.']
        for key in sorted(keys):
            lines.append(f'  {node_id(key)}["{label(nodes[key]["name"])}"]')
        for edge in public['relationships']:
            if edge['kind'] in edge_kinds and edge['from'] in keys and edge['to'] in keys:
                arrow = '-->' if edge['kind'] == 'github_parent' else '-.->'
                lines.append(f'  {node_id(edge["from"])} {arrow}|{label(edge.get("label", edge["kind"]))}| {node_id(edge["to"])}')
        return '\n'.join(lines) + '\n'
    result = {'hierarchy': chart({k for k in nodes if k.startswith('team:')}, {'github_parent'})}
    # Overview contains areas, not every access edge in the organization.
    lines = ['flowchart LR', 'accTitle: Pick Your AI area overview',
             'accDescr: Display grouping connects areas with approved teams, Projects and repositories. It does not describe GitHub nesting.']
    for a in public['areas']:
        aid = node_id('area:' + a['id'])
        lines.append(f'  {aid}["{label(a["name"])}"]')
        for kind, plural in [('team', 'teams'), ('repository', 'repositories'), ('project', 'projects')]:
            for rid in a[plural]:
                key = f'{kind}:{rid}'
                lines += [f'  {node_id(key)}["{label(nodes[key]["name"])}"]', f'  {aid} -.->|display grouping| {node_id(key)}']
        keys = {f'{kind}:{rid}' for kind, plural in [('team', 'teams'), ('repository', 'repositories'), ('project', 'projects')] for rid in a[plural]}
        result['area-' + a['id']] = chart(keys, {'github_parent', 'responsibility', 'project_link', 'project_responsibility'})
    result['overview'] = '\n'.join(lines) + '\n'
    return result


def private_hierarchy(model):
    """Full observed hierarchy, never a public artifact or roster."""
    lines = ['flowchart TB', 'accTitle: Complete observed GitHub team hierarchy']
    for team in model['teams']:
        lines.append(f'  {node_id(team["id"])}["{label(team["name"])}"]')
        if team['parent_id'] is not None:
            lines.append(f'  {node_id(team["parent_id"])} --> {node_id(team["id"])}')
    return '\n'.join(lines) + '\n'


def render(public, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    router.atomic_write(output / 'organization.json', router.dump(public))
    sources = charts(public)
    for name, source in sources.items():
        router.atomic_write(output / (name + '.mmd'), source)
    template = Path(__file__).with_name('directory.html').read_text(encoding='utf-8')
    rows = []
    for kind in ('teams', 'repositories', 'projects'):
        for row in public[kind]:
            areas = [a['name'] for a in public['areas'] if row['id'] in a[kind]]
            state = 'Unmapped display area' if not areas else ', '.join(areas)
            if kind == 'repositories':
                route = next((r for r in public['routing']['repositories'] if r['url'] == row['url']), None)
                if route:
                    state += ' · ' + '; '.join(l['level'].replace('_', ' ') + ': ' + l['disposition'].replace('_', ' ') for l in route['levels'])
            if row.get('archived') or row.get('closed'):
                state += ' · Archived / closed'
            if kind == 'projects':
                role = next(r for r in public['project_roles'] if r['project_id'] == row['id'])
                state += ' · operational assignment: ' + role['state']
            singular = {'teams': 'team', 'repositories': 'repository', 'projects': 'project'}[kind]
            rows.append(f'<tr data-kind="{kind}"><td>{singular}</td><th scope="row"><a href="{html.escape(row["url"], quote=True)}">{html.escape(row["name"])}</a></th><td>{html.escape(state)}</td></tr>')
    links = ''.join(f'<li><a href="{name}.mmd">{html.escape(name)} Mermaid</a> · <a href="{name}.svg">SVG</a> · <a href="{name}.png">PNG</a></li>' for name in sorted(sources))
    page = template.replace('<!--ROWS-->', '\n'.join(rows)).replace('<!--CHARTS-->', links)
    notices = ['Approved identities missing or withheld: ' + ', '.join(f'{k}: {len(public["unavailable_approved"][k])}' for k in ('teams', 'repositories', 'projects'))]
    notices += [r['name'] + ': ' + r['state'] for r in public['routing']['coordination_roles']]
    page = page.replace('<!--NOTICES-->', html.escape(' · '.join(notices)))
    page = page.replace('<!--OBSERVED-->', html.escape(public['observation']['completed_at']))
    for field in ('source_revision', 'policy_revision', 'mapping_revision'):
        page = page.replace('<!--' + field.upper() + '-->', html.escape(public['observation'][field]))
    router.atomic_write(output / 'index.html', page)
    router.atomic_write(output / 'directory.js', Path(__file__).with_name('directory.js').read_text(encoding='utf-8'))
    router.atomic_write(output / 'README.md', '# Current organization\n\n[Searchable directory](index.html) · [Model](organization.json) · [Overview](overview.svg)\n\nObservation: ' + public['observation']['completed_at'] + '\n\nThis is a generated approved-public projection, not a membership roster. Unmapped entities have unresolved responsibility. See [operation](../../ORGANIZATION.md).\n')
    return sources


def refresh(policy, mapping, state, output, source_revision, api=None, exporter=None):
    """Private durable state + staged public output; preserve last-good on failure.

    Caller publishes staged artifacts through the repository's reviewed PR path.
    This function never commits, pushes, modifies GitHub or sends notifications.
    """
    state, output = Path(state), Path(output)
    if any(path.is_symlink() for path in (output, *output.parents)):
        raise router.RoutingError('Artifact path must not contain symlinks')
    state, output = state.resolve(), output.resolve()
    if state == output or state in output.parents or output in state.parents:
        raise router.RoutingError('Private state and public output must not overlap')
    state.mkdir(parents=True, exist_ok=True)
    snapshot, status = state / 'model.json', state / 'status.json'
    with router.snapshot_lock(snapshot):
        previous = None
        try:
            if snapshot.exists():
                previous = router.read_json(snapshot)
                # Old policy may legitimately differ; verify persisted bytes.
                check = copy.deepcopy(previous)
                expected = check.pop('integrity_sha256', None)
                if expected != router.digest(check):
                    raise router.RoutingError('Corrupt cached model; reconcile before refresh')
            model = copy.deepcopy(collect(policy, mapping, source_revision, api))
            public = public_model(model, policy, mapping)
            if output.exists() and any(path.is_symlink() or not path.is_file() for path in output.iterdir()):
                raise router.RoutingError('Artifact must be a regular file')
            old_public = router.read_json(output / 'organization.json') if (output / 'organization.json').exists() else None
            changed = old_public is None or semantic(public) != semantic(old_public) or public['observation']['source_revision'] != old_public['observation']['source_revision'] or public['observation']['policy_revision'] != old_public['observation']['policy_revision'] or public['observation']['mapping_revision'] != old_public['observation']['mapping_revision']
            # Reconstruct every byte from trusted code, even for an unchanged
            # model. A pending artifact branch is input data, never proof that
            # its JavaScript or exports were actually generated by us.
            if not changed:
                # Copy only validated historical timestamps; all content and
                # other metadata still come from the new trusted projection.
                observed = old_public['observation']['completed_at']
                if router.timestamp(observed) > router.timestamp(public['observation']['completed_at']):
                    raise router.RoutingError('Historical observation is in the future')
                public['observation']['completed_at'] = observed
                prior_routing_time = old_public['routing']['snapshot_content_verified_at']
                if router.timestamp(prior_routing_time) > router.timestamp(model['observation']['completed_at']):
                    raise router.RoutingError('Historical routing observation is in the future')
                public['routing']['snapshot_content_verified_at'] = prior_routing_time
            output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=output.parent) as tmp:
                staged = Path(tmp) / 'public'
                sources = render(public, staged)
                if exporter is None:
                    raise router.RoutingError('An SVG/PNG exporter is required before publication')
                exporter(staged, sources)
                # Validate each export before touching current artifacts.
                for name in sources:
                    svg = (staged / (name + '.svg')).read_text(encoding='utf-8')
                    if not svg.lstrip().startswith('<svg') or 'foreignObject' in svg or '<script' in svg:
                        raise router.RoutingError('Invalid SVG export')
                    if not (staged / (name + '.png')).read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
                        raise router.RoutingError('Invalid PNG export')
                def files(directory):
                    if not directory.exists():
                        return None
                    if directory.is_symlink():
                        raise router.RoutingError('Artifact directory must not be a symlink')
                    result = {}
                    for path in directory.iterdir():
                        if path.is_symlink() or not path.is_file():
                            raise router.RoutingError('Artifact must be a regular file')
                        result[path.name] = path.read_bytes()
                    return result
                changed = files(staged) != files(output)
                # The caller works in an isolated checkout; publication is a
                # single Git tree update after this entire directory succeeds.
                backup = Path(tmp) / 'last-good'
                if changed and output.exists():
                    os.replace(output, backup)
                try:
                    if changed:
                        os.replace(staged, output)
                except OSError:
                    if backup.exists():
                        os.replace(backup, output)
                    raise
            model['integrity_sha256'] = router.digest(model)
            router.atomic_write(snapshot, router.dump(model), private=True)
            router.atomic_write(state / 'hierarchy.mmd', private_hierarchy(model), private=True)
            router.atomic_write(state / 'routing-snapshot.json', router.dump(model['routing']), private=True)
            router.atomic_write(state / 'routing-status.json', router.dump({
                'schema_version': 1, 'status': 'complete', 'attempted_at': model['observation']['completed_at'],
                'last_success_at': model['observation']['completed_at']}), private=True)
            router.atomic_write(status, router.dump({'status': 'complete', 'observed_at': model['observation']['completed_at'], 'changed': changed, 'content_sha256': semantic(public), 'published_at': None}), private=True)
            return changed
        except Exception:
            router.atomic_write(status, router.dump({'status': 'failed', 'attempted_at': router.now(), 'last_success_at': previous['observation']['completed_at'] if previous else None, 'detail': 'Refresh failed; last published content retained. Inspect private collector logs.'}), private=True)
            router.atomic_write(state / 'routing-status.json', router.dump({
                'schema_version': 1, 'status': 'failed', 'attempted_at': router.now(),
                'last_success_at': previous['observation']['completed_at'] if previous else None,
                'errors': [{'category': 'organization_refresh_failed', 'http_status': None}]}), private=True)
            raise


def mermaid_exporter(staged, sources):
    command = shutil.which('mmdc')
    if not command:
        raise router.RoutingError('Install pinned Mermaid CLI before exporting')
    # Neither the read token nor the publication token is a renderer input.
    renderer_env = {key: value for key, value in os.environ.items() if key in {
        'PATH', 'HOME', 'USERPROFILE', 'SYSTEMROOT', 'TEMP', 'TMP', 'TMPDIR',
        'LOCALAPPDATA', 'APPDATA', 'PUPPETEER_EXECUTABLE_PATH', 'PUPPETEER_CACHE_DIR',
    }}
    for name in sources:
        for suffix in ('svg', 'png'):
            subprocess.run([command, '-i', str(staged / (name + '.mmd')), '-o', str(staged / (name + '.' + suffix)),
                            '-c', str(Path(__file__).with_name('mermaid-config.json')), '-b', 'white'], check=True, capture_output=True, timeout=180, env=renderer_env)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', default='governance/escalation-policy.json')
    parser.add_argument('--mapping', default='governance/organization-mapping.json')
    parser.add_argument('--state', required=True, help='Private durable state outside checkout')
    parser.add_argument('--output', default='docs/organization/current')
    parser.add_argument('--source-revision', required=True)
    args = parser.parse_args()
    try:
        changed = refresh(router.read_json(args.policy), router.read_json(args.mapping), args.state, args.output, args.source_revision, exporter=mermaid_exporter)
        print('changed' if changed else 'unchanged')
    except Exception:
        print('Refresh failed; public output retained. See private status file.', file=__import__('sys').stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
