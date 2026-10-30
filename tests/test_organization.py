"""Synthetic organization fixtures; none represents actual people or policy."""
import copy
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from governance import organization as org
from test_router import policy, snapshot, REF
import test_router as routing_fixtures


def fixture():
    p = policy()
    s = snapshot(p)
    mapping = {'schema_version': 1, 'owner': 'example', 'decision_refs': [REF],
               'approved_public': {'teams': [10, 20, 30, 40, 50], 'repositories': [101], 'projects': ['P1', 'P2']},
               'areas': [{'id': 'example', 'name': 'Example area', 'teams': [10, 20], 'repositories': [101], 'projects': ['P1', 'P2'], 'decision_refs': [REF]}]}
    model = {'schema_version': 1, 'organization': p['organization'], 'routing': s,
             'teams': [{**t, 'members': t['direct_members']} for t in s['teams']],
             'repositories': [{**s['repositories'][0], 'name': 'example', 'archived': False}],
             'projects': [{'id': 'P1', 'number': 1, 'title': 'Example project', 'public': True, 'closed': False, 'repository_ids': [101]},
                          {'id': 'P2', 'number': 2, 'title': 'Other project', 'public': True, 'closed': True, 'repository_ids': [101]}],
             'observation': {'completed_at': '2026-01-01T12:00:01Z', 'source_revision': 'abc',
                             'policy_revision': org.router.digest(p), 'mapping_revision': org.router.digest(mapping), 'scope': 'synthetic', 'coverage': []}}
    return p, mapping, model


def fake_exporter(path, sources):
    for name in sources:
        (path / (name + '.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        (path / (name + '.png')).write_bytes(b'\x89PNG\r\n\x1a\nsynthetic')


class OrganizationTests(unittest.TestCase):
    def test_transport_decodes_real_utf8_pipe_on_windows(self):
        raw = json.dumps({'name': 'Project — café'}, ensure_ascii=False).encode('utf-8')
        def runner(args, **kwargs):
            self.assertEqual(kwargs['encoding'], 'utf-8')
            return subprocess.run([sys.executable, '-c', f'import sys; sys.stdout.buffer.write(bytes.fromhex("{raw.hex()}"))'], **kwargs)
        self.assertEqual(org.router.GitHub(runner=runner).get('orgs/Example')['name'], 'Project — café')

    def test_many_to_many_and_relationship_types(self):
        p, m, model = fixture()
        public = org.public_model(model, p, m)
        self.assertEqual(len([e for e in public['relationships'] if e['kind'] == 'project_link']), 2)
        self.assertEqual({e['kind'] for e in public['relationships']}, {'github_parent', 'access', 'responsibility', 'project_link'})
        self.assertEqual(public['unmapped']['teams'], [30, 40, 50])

    def test_unknown_is_not_inferred(self):
        p, m, model = fixture()
        model['teams'].append({'id': 99, 'name': 'unreviewed', 'slug': 'unreviewed', 'privacy': 'closed', 'parent_id': None})
        self.assertNotIn('unreviewed', json.dumps(org.public_model(model, p, m)))

    def test_private_data_excluded_even_if_approved(self):
        p, m, model = fixture()
        model['teams'][0]['privacy'] = 'secret'
        model['repositories'][0]['private'] = True
        model['projects'][0]['public'] = False
        text = json.dumps(org.public_model(model, p, m))
        for private in ('example-owner', 'person-', 'direct_members', 'team_grants', 'effective_permissions'):
            self.assertNotIn(private, text)
        self.assertFalse(org.public_model(model, p, m)['repositories'])

    def test_rename_preserves_identity(self):
        p, m, model = fixture()
        before = org.public_model(model, p, m)
        model['teams'][0]['name'] = 'Renamed'
        after = org.public_model(model, p, m)
        self.assertEqual(before['relationships'], after['relationships'])
        self.assertNotEqual(org.semantic(before), org.semantic(after))

    def test_repository_rename_retains_routing_by_id(self):
        p, m, model = fixture()
        model['repositories'][0]['full_name'] = 'ExampleOrg/renamed'
        model['routing']['repositories'][0]['full_name'] = 'ExampleOrg/renamed'
        routing_fixtures.seal(model['routing'], p)
        public = org.public_model(model, p, m)
        self.assertEqual(public['routing']['repositories'][0]['url'], 'https://github.com/ExampleOrg/renamed')

    def test_cycles_and_missing_parent_rejected(self):
        for parent in (10, 999):
            p, m, model = fixture()
            model['teams'][0]['parent_id'] = parent
            with self.assertRaises(org.router.RoutingError):
                org.validate_model(model, p, m)

    def test_invalid_mapping_rejected(self):
        p, m, model = fixture()
        m['areas'][0]['teams'].append(999)
        with self.assertRaises(org.router.RoutingError):
            org.validate_mapping(m, p)

    def test_unsafe_names_escaped(self):
        p, m, model = fixture()
        model['teams'][0]['name'] = '<script>alert("x")</script>\n%%{init:evil}'
        public = org.public_model(model, p, m)
        with tempfile.TemporaryDirectory() as tmp:
            sources = org.render(public, tmp)
            self.assertNotIn('<script>alert', Path(tmp, 'index.html').read_text())
            self.assertNotIn('%%{init', sources['hierarchy'])

    def test_deterministic_and_observation_noop(self):
        p, m, model = fixture()
        public = org.public_model(model, p, m)
        changed = copy.deepcopy(public)
        changed['observation']['completed_at'] = '2026-01-02T00:00:00Z'
        self.assertEqual(org.semantic(public), org.semantic(changed))
        self.assertEqual(org.charts(public), org.charts(copy.deepcopy(public)))

    def test_refresh_noop_and_failure_recovery(self):
        p, m, model = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            state, output = Path(tmp, 'state'), Path(tmp, 'public')
            with patch.object(org, 'collect', return_value=model):
                self.assertTrue(org.refresh(p, m, state, output, 'abc', exporter=fake_exporter))
                self.assertFalse(org.refresh(p, m, state, output, 'abc', exporter=fake_exporter))
            before = {x.name: x.read_bytes() for x in output.iterdir()}
            with patch.object(org, 'collect', side_effect=org.router.APIError('teams', 'access_denied', 403)):
                with self.assertRaises(org.router.RoutingError):
                    org.refresh(p, m, state, output, 'abc', exporter=fake_exporter)
            self.assertEqual(before, {x.name: x.read_bytes() for x in output.iterdir()})
            self.assertEqual(json.loads((state / 'status.json').read_text())['status'], 'failed')
            snapshot_with_status = org.router.attach_refresh_status(org.router.read_json(state / 'routing-snapshot.json'), state / 'routing-status.json')
            route = org.router.resolve(p, snapshot_with_status, 'ExampleOrg/example', max_age_seconds=999999999)
            self.assertEqual(route['freshness']['status'], 'refresh_failed')
            self.assertTrue(all(not level['recipients'] for level in route['levels']))
            with patch.object(org, 'collect', return_value=model):
                org.refresh(p, m, state, output, 'abc', exporter=fake_exporter)
            self.assertEqual(json.loads((state / 'status.json').read_text())['status'], 'complete')

    def test_export_failure_preserves_output(self):
        p, m, model = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            state, output = Path(tmp, 'state'), Path(tmp, 'public')
            output.mkdir(); (output / 'sentinel').write_text('last good')
            with patch.object(org, 'collect', return_value=model):
                with self.assertRaises(RuntimeError):
                    org.refresh(p, m, state, output, 'abc', exporter=lambda *_: (_ for _ in ()).throw(RuntimeError()))
            self.assertEqual((output / 'sentinel').read_text(), 'last good')

    def test_project_pagination_and_duplicate_detection(self):
        class API:
            coverage = []
            def __init__(self, repeat=False): self.n = 0; self.repeat = repeat
            def _call(self, args, resource):
                self.n += 1
                return {'nodes': [{'id': 'first' if self.n == 1 or self.repeat else 'second'}],
                        'pageInfo': {'hasNextPage': self.n == 1, 'endCursor': 'next'}}
        self.assertEqual(len(org.connection(API(), org.PROJECTS, {}, lambda x: x, 'id')), 2)
        with self.assertRaises(org.router.RoutingError):
            org.connection(API(True), org.PROJECTS, {}, lambda x: x, 'id')

    def test_missing_access_is_not_empty(self):
        class API:
            def _call(self, *_): raise org.router.APIError('projects', 'access_denied', 403)
        with self.assertRaises(org.router.APIError):
            org.connection(API(), org.PROJECTS, {}, lambda x: x, 'id')

    def test_hierarchy_edges_match_model(self):
        p, m, model = fixture()
        public = org.public_model(model, p, m)
        actual = {(e['from'], e['to']) for e in public['relationships'] if e['kind'] == 'github_parent'}
        expected = {(f"team:{t['parent_id']}", f"team:{t['id']}") for t in model['teams'] if t['parent_id'] is not None}
        self.assertEqual(actual, expected)

    def test_complete_collection_shares_routing_observation(self):
        class Source(routing_fixtures.CollectionTests.Source):
            def get(self, endpoint):
                result = super().get(endpoint)
                if endpoint == 'orgs/ExampleOrg': result['node_id'] = 'ORG'
                return result
            def pages(self, endpoint):
                if endpoint == 'orgs/ExampleOrg/teams':
                    return [{**t, 'node_id': 'T' + str(t['id']), 'parent': {'id': t['parent_id']} if t['parent_id'] else None} for t in self.data['teams']]
                if endpoint == 'orgs/ExampleOrg/repos':
                    return [{'id': 101, 'node_id': 'REPO101', 'name': 'example', 'full_name': 'ExampleOrg/example', 'private': False, 'visibility': 'public', 'archived': False}]
                return super().pages(endpoint)
            def _call(self, args, resource):
                if 'query=' + org.PROJECTS in args:
                    return {'data': {'organization': {'id': 'ORG', 'projectsV2': {'nodes': [], 'pageInfo': {'hasNextPage': False}}}}}
                raise AssertionError(args)
        p, m, _ = fixture()
        model = org.collect(p, m, 'synthetic', Source())
        self.assertEqual(len(model['teams']), 5)
        self.assertEqual(model['routing']['teams'][0]['direct_members'], model['teams'][0]['members'])
        public = org.public_model(model, p, m)
        self.assertEqual(public['unavailable_approved']['projects'], ['P1', 'P2'])

    def test_corrupt_cache_and_overlap_fail_closed(self):
        p, m, _ = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp, 'state'); state.mkdir()
            (state / 'model.json').write_text('{broken')
            with self.assertRaises(org.router.RoutingError):
                org.refresh(p, m, state, Path(tmp, 'output'), 'test')
            with self.assertRaises(org.router.RoutingError):
                org.refresh(p, m, state, state / 'public', 'test')


if __name__ == '__main__': unittest.main()
