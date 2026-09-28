"""Scenario snapshots. Register this router in api_router.py.

Save is the ONLY endpoint here that runs a simulation and creates a scenario.
/simulation/run remains calculation-only.
"""
import json
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from database import engine
from models.simulation import SimulationRequest
from simulation.runner import run

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


class SaveScenario(BaseModel):
    scenario_name: str = Field(min_length=1, max_length=100)
    line_type: Literal["Gigafactory", "Pilot Line"]
    configuration: SimulationRequest


class BaselineSelection(BaseModel):
    # Explicitly selecting a scenario's own line type avoids cross-line SoA assignments.
    line_type: Literal["Gigafactory", "Pilot Line"]


def _json(value):
    return json.dumps(value, default=str, allow_nan=False)


def _config_dict(model):
    return model.model_dump(mode="json") if hasattr(model, "model_dump") else model.dict()


def _row(row):
    return dict(row._mapping) if row is not None else None


@router.post("", status_code=201)
def save_scenario(payload: SaveScenario):
    name = payload.scenario_name.strip()
    if not name:
        raise HTTPException(422, "Scenario name cannot be empty")
    configuration = _config_dict(payload.configuration)
    # Recompute from the submitted configuration, never trust a stale browser result.
    result = run(payload.configuration)
    overall = result["overall"]
    capacity = result["capacity"]
    throughput = capacity.get("required_good_cells_day")
    if throughput is None:
        raise HTTPException(500, "Simulation result has no daily throughput")
    route_json = {**configuration, "snapshot_version": 1}
    with engine.begin() as conn:
        scenario_id = conn.execute(text("""
            INSERT INTO public.scenario (scenario_name, line_type, route_json)
            VALUES (:name, :line_type, CAST(:route_json AS jsonb))
            RETURNING scenario_id
        """), {"name": name, "line_type": payload.line_type,
               "route_json": _json(route_json)}).scalar_one()
        # node_id is a deterministic 1-based ordinal across the three branches.
        ordinal = 0
        for branch in ("cathode_route", "anode_route", "assembly_route"):
            for step in configuration[branch]:
                ordinal += 1
                equipment_id = step.get("equipment_id") or step.get("technology_id")
                if equipment_id is None:
                    raise HTTPException(422, f"Missing equipment for {branch} step {ordinal}")
                conn.execute(text("""
                    INSERT INTO public.scenario_equipment (scenario_id, node_id, equipment_id)
                    VALUES (:scenario_id, :node_id, :equipment_id)
                """), {"scenario_id": scenario_id, "node_id": ordinal,
                       "equipment_id": equipment_id})
        conn.execute(text("""
            INSERT INTO public.scenario_result
                (scenario_id, total_cost, total_energy, total_carbon, throughput, result_json)
            VALUES (:scenario_id, :cost, :energy, :carbon, :throughput, CAST(:result AS jsonb))
        """), {"scenario_id": scenario_id, "cost": overall["costs"]["total"],
               "energy": overall["energy"]["total"], "carbon": overall["carbon"]["total"],
               "throughput": throughput, "result": _json(result)})
    return {"scenario_id": scenario_id, "result": result}


@router.get("")
def list_scenarios():
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT s.scenario_id, s.scenario_name, s.line_type, s.created_at,
                   r.total_cost, r.total_energy, r.total_carbon, r.throughput,
                   (b.scenario_id IS NOT NULL) AS is_soa
            FROM public.scenario s
            LEFT JOIN public.scenario_result r ON r.scenario_id = s.scenario_id
            LEFT JOIN public.scenario_baseline b ON b.scenario_id = s.scenario_id
            ORDER BY s.created_at DESC, s.scenario_id DESC
        """)).all()
    return [_row(row) for row in rows]


@router.get("/{scenario_id}")
def get_scenario(scenario_id: int):
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT s.scenario_id, s.scenario_name, s.line_type, s.created_at,
                   s.route_json, r.result_json, r.total_cost, r.total_energy,
                   r.total_carbon, r.throughput,
                   (b.scenario_id IS NOT NULL) AS is_soa
            FROM public.scenario s
            LEFT JOIN public.scenario_result r ON r.scenario_id = s.scenario_id
            LEFT JOIN public.scenario_baseline b ON b.scenario_id = s.scenario_id
            WHERE s.scenario_id = :id
        """), {"id": scenario_id}).first()
    if row is None:
        raise HTTPException(404, "Scenario not found")
    return _row(row)


@router.delete("/{scenario_id}")
def delete_scenario(scenario_id: int):
    with engine.begin() as conn:
        deleted = conn.execute(text("""
            DELETE FROM public.scenario WHERE scenario_id = :id RETURNING scenario_id
        """), {"id": scenario_id}).scalar_one_or_none()
    if deleted is None:
        raise HTTPException(404, "Scenario not found")
    return {"status": "deleted", "scenario_id": scenario_id}


@router.put("/{scenario_id}/soa")
def assign_soa(scenario_id: int, payload: BaselineSelection):
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT line_type FROM public.scenario WHERE scenario_id = :id FOR UPDATE
        """), {"id": scenario_id}).first()
        if row is None:
            raise HTTPException(404, "Scenario not found")
        if row.line_type != payload.line_type:
            raise HTTPException(422, "SoA line type must match the scenario line type")
        # Clear this scenario's former designation if any, then replace the line's SoA.
        conn.execute(text("DELETE FROM public.scenario_baseline WHERE scenario_id = :id"),
                     {"id": scenario_id})
        conn.execute(text("""
            INSERT INTO public.scenario_baseline (line_type, scenario_id)
            VALUES (:line_type, :id)
            ON CONFLICT (line_type) DO UPDATE
            SET scenario_id = EXCLUDED.scenario_id, assigned_at = CURRENT_TIMESTAMP
        """), {"line_type": payload.line_type, "id": scenario_id})
    return {"scenario_id": scenario_id, "line_type": payload.line_type, "is_soa": True}


@router.delete("/{scenario_id}/soa")
def remove_soa(scenario_id: int):
    with engine.begin() as conn:
        deleted = conn.execute(text("""
            DELETE FROM public.scenario_baseline WHERE scenario_id = :id RETURNING scenario_id
        """), {"id": scenario_id}).scalar_one_or_none()
    if deleted is None:
        raise HTTPException(404, "SoA designation not found")
    return {"scenario_id": scenario_id, "is_soa": False}
