"""Project-wide display labels; scenario/record IDs never determine labels."""
import json
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from auth import current_user
from database import engine

router = APIRouter(prefix='/parameter-labels', tags=['parameter labels'], dependencies=[Depends(current_user)])

class ResolveLabels(BaseModel):
    identifiers: list[str] = Field(max_length=2000)


def parameter_identity(identifier):
    try:
        parts = json.loads(identifier)
    except (ValueError, TypeError):
        raise HTTPException(422, 'Invalid matrix parameter identifier')
    if not isinstance(parts, list) or not all(isinstance(part, str) for part in parts):
        raise HTTPException(422, 'Invalid matrix parameter identifier')
    if len(parts) == 2 and parts[0] == 'equipment' and parts[1].strip():
        key, prefix = parts, 'P'
    elif len(parts) == 3 and parts[0] in ('production_configuration', 'product_configuration') and parts[2].strip():
        key = [parts[0], parts[2]]
        prefix = 'IP' if parts[0] == 'product_configuration' else 'P'
    else:
        raise HTTPException(422, 'Unsupported matrix parameter identifier')
    if len(identifier) > 2048:
        raise HTTPException(422, 'Matrix parameter identifier is too long')
    return json.dumps(key, separators=(',', ':'), ensure_ascii=False), prefix


def require_enabled():
    if os.getenv('SHARED_PARAMETER_LABELS_ENABLED', '').lower() != 'true':
        raise HTTPException(503, 'Shared parameter labels are not enabled yet')


def resolve_labels(conn, identifiers):
    identities = {identifier: parameter_identity(identifier) for identifier in identifiers}
    # Serialize allocations across requests; one transaction allocates and returns
    # every entry, with uniqueness constraints as a second line of protection.
    conn.execute(text("SELECT pg_advisory_xact_lock(736218905)"))
    codes = {}
    for identifier, (key, prefix) in sorted(identities.items(), key=lambda item: item[1][0]):
        number = conn.execute(text('SELECT label_number FROM public.parameter_label_registry WHERE parameter_key=:key'), {'key': key}).scalar_one_or_none()
        if number is None:
            number = conn.execute(text('''INSERT INTO public.parameter_label_registry(parameter_key,prefix,label_number)
                SELECT :key,:prefix,COALESCE(MAX(label_number),0)+1
                FROM public.parameter_label_registry WHERE prefix=:prefix
                RETURNING label_number'''), {'key': key, 'prefix': prefix}).scalar_one()
        codes[identifier] = f'{prefix}{number:02d}'
    return codes


@router.post('/resolve')
def resolve(payload: ResolveLabels):
    require_enabled()
    # Validate all identifiers before starting a database transaction.
    for identifier in payload.identifiers:
        parameter_identity(identifier)
    with engine.begin() as conn:
        return {'labels': resolve_labels(conn, payload.identifiers)}
