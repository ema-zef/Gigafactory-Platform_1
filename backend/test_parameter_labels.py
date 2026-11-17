"""Offline tests for shared, append-only P/IP labels. No database connection."""
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import HTTPException

with patch.dict(os.environ, {'DATABASE_URL': 'sqlite://'}):
    from routes import parameter_label_routes as labels


class Store:
    def __init__(self):
        self.entries = {}
        self.locks = 0
    def execute(self, statement, params=None):
        sql = str(statement)
        if 'pg_advisory_xact_lock' in sql:
            self.locks += 1
            return None
        if sql.startswith('SELECT label_number'):
            item = self.entries.get(params['key'])
            return SimpleNamespace(scalar_one_or_none=lambda: item[1] if item else None)
        if sql.startswith('INSERT INTO'):
            assert self.locks > 0
            number = max([number for prefix, number in self.entries.values() if prefix == params['prefix']], default=0) + 1
            self.entries[params['key']] = (params['prefix'], number)
            return SimpleNamespace(scalar_one=lambda: number)
        raise AssertionError(sql)


def identifier(*parts):
    return json.dumps(parts)


class ParameterLabelTests(unittest.TestCase):
    def test_reuses_labels_across_scenarios_with_gaps_new_parameters_and_changed_record_ids(self):
        store = Store()
        speed = identifier('equipment', 'Mixing_Speed')
        temperature = identifier('equipment', 'Drying_Temperature')
        product = identifier('product_configuration', '1', 'porosity')
        first = labels.resolve_labels(store, [speed, temperature, product])
        second_product = identifier('product_configuration', '99', 'porosity')
        capacity = identifier('product_configuration', '99', 'cell_capacity_kwh')
        extra = identifier('equipment', 'Coating_Thickness')
        second = labels.resolve_labels(store, [extra, second_product, speed, capacity])
        self.assertEqual(first[speed], second[speed])
        self.assertEqual(first[product], second[second_product])
        self.assertTrue(first[product].startswith('IP'))
        self.assertTrue(second[capacity].startswith('IP'))
        self.assertTrue(second[extra].startswith('P'))
        self.assertNotEqual(second[extra], first[temperature])
        self.assertIn(labels.parameter_identity(temperature)[0], store.entries)
        again = labels.resolve_labels(store, [temperature, speed])
        self.assertEqual(again[temperature], first[temperature])
        self.assertEqual(again[speed], first[speed])
        self.assertEqual(store.locks, 3)
        self.assertEqual(len(store.entries), 5)

    def test_product_and_production_use_separate_identities_and_prefixes(self):
        store = Store()
        product = identifier('product_configuration', '1', 'density')
        production = identifier('production_configuration', '1', 'density')
        codes = labels.resolve_labels(store, [product, production])
        self.assertEqual(codes[product], 'IP01')
        self.assertEqual(codes[production], 'P01')
        self.assertEqual(labels.parameter_identity(identifier('production_configuration', '2', 'density')), labels.parameter_identity(production))

    def test_order_and_duplicate_identifiers_do_not_reallocate_labels(self):
        ids = [identifier('equipment', name) for name in ['Mixing_Speed', 'Drying_Temperature']]
        a, b = Store(), Store()
        self.assertEqual(labels.resolve_labels(a, ids), labels.resolve_labels(b, list(reversed(ids))))
        before = dict(a.entries)
        labels.resolve_labels(a, ids + ids)
        self.assertEqual(a.entries, before)

    def test_rejects_invalid_identifiers(self):
        for value in ['not json', 'null', '[]', '[1,2]', identifier('equipment', ''), identifier('unknown', 'x'), identifier('equipment', 'x', 'y')]:
            with self.subTest(value=value), self.assertRaises(HTTPException):
                labels.parameter_identity(value)

    def test_disabled_feature_never_opens_database(self):
        with patch.dict(os.environ, {'SHARED_PARAMETER_LABELS_ENABLED': 'false'}), patch.object(labels, 'engine') as engine:
            with self.assertRaises(HTTPException) as error:
                labels.resolve(labels.ResolveLabels(identifiers=[]))
            self.assertEqual(error.exception.status_code, 503)
            engine.begin.assert_not_called()

    def test_endpoint_requires_sign_in(self):
        self.assertTrue(any(dependency.dependency is labels.current_user for dependency in labels.router.dependencies))
        with self.assertRaises(HTTPException) as error:
            labels.current_user(None)
        self.assertEqual(error.exception.status_code, 401)

    def test_all_identifiers_validated_before_transaction(self):
        with patch.dict(os.environ, {'SHARED_PARAMETER_LABELS_ENABLED': 'true'}), patch.object(labels, 'engine') as engine:
            with self.assertRaises(HTTPException):
                labels.resolve(labels.ResolveLabels(identifiers=[identifier('equipment', 'Mixing_Speed'), 'invalid']))
            engine.begin.assert_not_called()

if __name__ == '__main__':
    unittest.main()
