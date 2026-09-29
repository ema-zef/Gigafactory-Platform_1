"""Private scenarios and two administrator-published, immutable SOTA snapshots."""
import json
from decimal import Decimal
from datetime import date, datetime, time
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from auth import User, admin_only, current_user
from database import engine
from models.simulation import SimulationRequest
from simulation.runner import run
from simulation_access import inputs

router = APIRouter(prefix='/scenarios', tags=['scenarios'])

class SaveScenario(BaseModel):
    scenario_name: str = Field(min_length=1, max_length=100)
    line_type: Literal['Gigafactory', 'Pilot Line']
    configuration: SimulationRequest

class BaselineSelection(BaseModel):
    line_type: Literal['Gigafactory', 'Pilot Line']


def json_value(value):
    return json.dumps(value, default=lambda obj: float(obj) if isinstance(obj, Decimal) else obj.isoformat() if isinstance(obj, (date, datetime, time)) else str(obj), allow_nan=False)


def as_dict(row):
    return dict(row._mapping) if row else None


def access_clause(user):
    if user.is_admin:
        return 'TRUE'
    return "(s.owner_id=:owner OR EXISTS (SELECT 1 FROM public.scenario_baseline b JOIN public.sota_publication p ON p.scenario_id=b.scenario_id WHERE b.scenario_id=s.scenario_id))"

@router.post('', status_code=201)
def save_scenario(payload: SaveScenario, user: User = Depends(current_user)):
    configuration = payload.configuration.model_dump(mode='json')
    result = run(payload.configuration, user)
    overall, capacity = result['overall'], result['capacity']
    throughput = capacity.get('required_good_cells_day')
    if throughput is None:
        raise HTTPException(500, 'Simulation result has no daily throughput')
    with engine.begin() as conn:
        scenario_id = conn.execute(text('''INSERT INTO public.scenario(scenario_name,line_type,route_json,owner_id)
          VALUES (:name,:line_type,CAST(:route AS jsonb),:owner) RETURNING scenario_id'''),
          {'name': payload.scenario_name.strip(), 'line_type': payload.line_type, 'route': json_value({**configuration,'snapshot_version':2}), 'owner':user.id}).scalar_one()
        ordinal = 0
        for branch in ('cathode_route','anode_route','assembly_route'):
            for step in configuration[branch]:
                ordinal += 1
                conn.execute(text('INSERT INTO public.scenario_equipment(scenario_id,node_id,equipment_id) VALUES (:scenario,:node,:equipment)'), {'scenario':scenario_id,'node':ordinal,'equipment':step['technology_id']})
        conn.execute(text('''INSERT INTO public.scenario_result(scenario_id,total_cost,total_energy,total_carbon,throughput,result_json)
          VALUES (:id,:cost,:energy,:carbon,:throughput,CAST(:result AS jsonb))'''),
          {'id':scenario_id,'cost':overall['costs']['total'],'energy':overall['energy']['total'], 'carbon':overall['carbon']['total'],'throughput':throughput,'result':json_value(result)})
    return {'scenario_id':scenario_id,'result':result}

@router.get('')
def list_scenarios(user: User = Depends(current_user)):
    with engine.connect() as conn:
        rows = conn.execute(text(f'''SELECT s.scenario_id,s.scenario_name,s.line_type,s.created_at,s.owner_id,
          r.total_cost,r.total_energy,r.total_carbon,r.throughput,
          (b.scenario_id IS NOT NULL) AS is_soa
          FROM public.scenario s LEFT JOIN public.scenario_result r ON r.scenario_id=s.scenario_id
          LEFT JOIN public.scenario_baseline b ON b.scenario_id=s.scenario_id
          LEFT JOIN public.sota_publication p ON p.scenario_id=s.scenario_id
          WHERE {access_clause(user)} ORDER BY s.created_at DESC,s.scenario_id DESC'''), {'owner':user.id}).all()
    return [dict(as_dict(row), can_delete=(user.is_admin or str(row.owner_id)==user.id) and not row.is_soa) for row in rows]

@router.get('/{scenario_id}')
def get_scenario(scenario_id: int, user: User = Depends(current_user)):
    with engine.connect() as conn:
        row = conn.execute(text(f'''SELECT s.scenario_id,s.scenario_name,s.line_type,s.created_at,s.owner_id,s.route_json,
          r.result_json,r.total_cost,r.total_energy,r.total_carbon,r.throughput,
          (b.scenario_id IS NOT NULL) AS is_soa
          FROM public.scenario s LEFT JOIN public.scenario_result r ON r.scenario_id=s.scenario_id
          LEFT JOIN public.scenario_baseline b ON b.scenario_id=s.scenario_id
          LEFT JOIN public.sota_publication p ON p.scenario_id=s.scenario_id
          WHERE s.scenario_id=:id AND {access_clause(user)}'''), {'id':scenario_id,'owner':user.id}).first()
    if not row:
        raise HTTPException(404,'Scenario not found')
    return dict(as_dict(row), can_delete=(user.is_admin or str(row.owner_id)==user.id) and not row.is_soa)

@router.delete('/{scenario_id}')
def delete_scenario(scenario_id: int, user: User = Depends(current_user)):
    with engine.begin() as conn:
        row = conn.execute(text('SELECT owner_id FROM public.scenario WHERE scenario_id=:id FOR UPDATE'),{'id':scenario_id}).first()
        if not row or (not user.is_admin and str(row.owner_id)!=user.id):
            raise HTTPException(404,'Scenario not found')
        if conn.execute(text('SELECT 1 FROM public.scenario_baseline WHERE scenario_id=:id'),{'id':scenario_id}).first():
            raise HTTPException(409,'Remove the SOTA designation before deleting the scenario')
        conn.execute(text('DELETE FROM public.scenario WHERE scenario_id=:id'),{'id':scenario_id})
    return {'status':'deleted','scenario_id':scenario_id}

@router.put('/{scenario_id}/soa')
def publish_sota(scenario_id: int, payload: BaselineSelection, user: User = Depends(admin_only)):
    # Build immutable snapshots from the exact inputs used by the saved simulation.
    with engine.begin() as conn:
        row = conn.execute(text('SELECT line_type,owner_id,route_json FROM public.scenario WHERE scenario_id=:id FOR UPDATE'),{'id':scenario_id}).mappings().first()
        if not row:
            raise HTTPException(404,'Scenario not found')
        if row['line_type'] != payload.line_type:
            raise HTTPException(422,'SOTA line type must match scenario line type')
        if row['owner_id'] is not None and str(row['owner_id']) != user.id:
            raise HTTPException(403,'Only your own scenarios can be published as SOTA')
        config = row['route_json']
        if not config or not config.get('product_id') or not config.get('plant_id'):
            raise HTTPException(422,'Legacy scenario has no unique source IDs. Rerun and save it before publishing.')
        request = SimulationRequest(**{k:v for k,v in config.items() if k != 'snapshot_version'})
        product, material, plant, equipment = inputs(request,user)
        source_rows = [product,material,plant,*equipment.values()]
        if any(r.get('owner_id') is not None and str(r['owner_id']) != user.id for r in source_rows):
            raise HTTPException(403,'A SOTA cannot publish another user\'s private data')
        snapshot = {'product_configuration':[product],'product_material':[material],
                    'production_configuration':[plant],'equipment':list(equipment.values())}
        if conn.execute(text('SELECT 1 FROM public.sota_publication WHERE scenario_id=:id'), {'id':scenario_id}).first():
            raise HTTPException(409, 'This scenario was already published. Save a new scenario to publish a new version.')
        conn.execute(text('''INSERT INTO public.sota_publication(scenario_id,line_type,source_snapshot)
          VALUES (:id,:line_type,CAST(:snapshot AS jsonb))'''),
          {'id':scenario_id,'line_type':payload.line_type,'snapshot':json_value(snapshot)})
        conn.execute(text('DELETE FROM public.scenario_baseline WHERE scenario_id=:id'),{'id':scenario_id})
        conn.execute(text('''INSERT INTO public.scenario_baseline(line_type,scenario_id) VALUES (:line_type,:id)
          ON CONFLICT(line_type) DO UPDATE SET scenario_id=EXCLUDED.scenario_id,assigned_at=now()'''),
          {'line_type':payload.line_type,'id':scenario_id})
    return {'scenario_id':scenario_id,'line_type':payload.line_type,'is_soa':True}

@router.delete('/{scenario_id}/soa')
def unpublish_sota(scenario_id: int, user: User = Depends(admin_only)):
    with engine.begin() as conn:
        deleted = conn.execute(text('DELETE FROM public.scenario_baseline WHERE scenario_id=:id RETURNING scenario_id'),{'id':scenario_id}).scalar_one_or_none()
    if deleted is None:
        raise HTTPException(404,'SOTA designation not found')
    return {'scenario_id':scenario_id,'is_soa':False}
