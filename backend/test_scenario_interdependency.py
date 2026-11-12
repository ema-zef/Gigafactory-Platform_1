"""Offline scenario relationship tests using an in-memory JSONB boundary."""
import json
import os
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

from pydantic import ValidationError

# The route imports the database module. Its fallback engine is local and the
# route engine and simulation are both replaced before calling either handler.
with patch.dict(os.environ, {"DATABASE_URL": "sqlite://"}):
    from routes import scenario_routes


RELATIONSHIPS = [
    {"source": '["equipment","Mixing_Speed"]', "target": "Temperature", "direction": "increase"},
    {"source": "Temperature", "target": '["equipment","Mixing_Speed"]', "direction": "decrease"},
]
SIMULATION_RESULT = {
    "overall": {
        "costs": {"total": 1},
        "energy": {"total": 2},
        "carbon": {"total": 3},
    },
    "capacity": {"required_good_cells_day": 4},
}


class ScenarioStore:
    def __init__(self, test):
        self.test = test
        self.scenarios = {}

    @contextmanager
    def begin(self):
        yield self

    @contextmanager
    def connect(self):
        yield self

    def execute(self, statement, params):
        sql = " ".join(str(statement).split())
        if sql.startswith("INSERT INTO public.scenario("):
            self.test.assertIn("interdependency_relationships", sql)
            self.test.assertIn("CAST(:relationships AS jsonb)", sql)
            scenario_id = len(self.scenarios) + 1
            self.scenarios[scenario_id] = {
                "scenario_id": scenario_id,
                "owner_id": params["owner"],
                "is_soa": False,
                "interdependency_relationships": json.loads(params["relationships"]),
            }
            return SimpleNamespace(scalar_one=lambda: scenario_id)
        if sql.startswith("INSERT INTO public.scenario_result("):
            self.test.assertIn(params["id"], self.scenarios)
            return None
        if sql.startswith("SELECT s.scenario_id,"):
            self.test.assertIn("s.interdependency_relationships", sql)
            self.test.assertIn("s.scenario_id=:id", sql)
            self.test.assertIn("s.owner_id=:owner", sql)
            stored = self.scenarios.get(params["id"])
            row = None
            if stored and stored["owner_id"] == params["owner"]:
                row = SimpleNamespace(_mapping=stored, **stored)
            return SimpleNamespace(first=lambda: row)
        self.test.fail(f"Unexpected database statement: {sql}")


class ScenarioInterdependencyTests(unittest.TestCase):
    def payload(self, **fields):
        return scenario_routes.SaveScenario(
            scenario_name="Offline scenario",
            line_type="Gigafactory",
            configuration={
                "plant_code": "P", "product_code": "C", "plant_id": 1, "product_id": 2,
            },
            **fields,
        )

    def test_save_reload_preserves_relationships_and_default_empty_list(self):
        user = scenario_routes.User(id="owner", username="offline", role="user")
        store = ScenarioStore(self)
        with (
            patch.object(scenario_routes, "engine", store),
            patch.object(scenario_routes, "run", return_value=SIMULATION_RESULT),
        ):
            for fields, expected in [
                ({"interdependency_relationships": RELATIONSHIPS}, RELATIONSHIPS),
                ({}, []),
            ]:
                with self.subTest(fields=fields):
                    saved = scenario_routes.save_scenario(self.payload(**fields), user)
                    loaded = scenario_routes.get_scenario(saved["scenario_id"], user)
                    self.assertEqual(loaded["interdependency_relationships"], expected)
            reloaded = scenario_routes.get_scenario(1, user)
            self.assertEqual(reloaded["interdependency_relationships"], RELATIONSHIPS)

    def test_identifiers_are_trimmed(self):
        relationship = self.payload(interdependency_relationships=[
            {"source": " A ", "target": " B ", "direction": "increase"},
        ]).interdependency_relationships[0]
        self.assertEqual((relationship.source, relationship.target), ("A", "B"))

    def test_rejects_invalid_relationships(self):
        cases = [
            ([{"source": "A", "target": "B", "direction": "both"}], "direction"),
            ([{"source": " ", "target": "B", "direction": "increase"}], "source"),
            ([{"source": "A", "target": "", "direction": "increase"}], "target"),
            ([{"source": "A", "target": " A ", "direction": "increase"}], "reference itself"),
            ([
                {"source": "A", "target": "B", "direction": "increase"},
                {"source": " A ", "target": "B", "direction": "decrease"},
            ], "Duplicate interdependency"),
        ]
        for relationships, message in cases:
            with self.subTest(relationships=relationships):
                with self.assertRaisesRegex(ValidationError, message):
                    self.payload(interdependency_relationships=relationships)


if __name__ == "__main__":
    unittest.main()
