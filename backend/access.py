"""Only whitelisted tables/columns. Public SOTA rows are immutable snapshots."""
from fastapi import HTTPException
from sqlalchemy import text
from database import engine

TABLES = {
    'equipment': ('id', None),
    'product_configuration': ('row_id', 'productcode'),
    'product_material': ('seq', 'productcode'),
    'production_configuration': ('id', 'code'),
}


def columns(conn, table):
    if table not in TABLES:
        raise HTTPException(404, 'Unknown resource')
    return {r['column_name']: r for r in conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name=:table"), {'table': table}).mappings()}


def snapshot_rows(conn, table):
    return conn.execute(text("""
      SELECT p.source_snapshot -> :table AS items, p.line_type
      FROM public.sota_publication p
      JOIN public.scenario_baseline b ON b.scenario_id=p.scenario_id AND b.line_type=p.line_type
      WHERE p.source_snapshot ? :table
    """), {'table': table}).mappings().all()


def visible_rows(table, user):
    pk, _ = TABLES[table]
    with engine.connect() as conn:
        if user.is_admin:
            rows = conn.execute(text(f'SELECT * FROM public.{table} ORDER BY "{pk}"')).mappings().all()
        else:
            rows = conn.execute(text(f'SELECT * FROM public.{table} WHERE owner_id=:owner ORDER BY "{pk}"'), {'owner': user.id}).mappings().all()
        result = [dict(r, is_sota=False, read_only=False) for r in rows]
        if not user.is_admin:
            seen = {r[pk] for r in result}
            for publication in snapshot_rows(conn, table):
                for record in publication['items'] or []:
                    if record[pk] not in seen:
                        result.append({**{k:v for k,v in record.items() if k != 'owner_id'}, 'is_sota': True, 'read_only': True, 'sota_line_type': publication['line_type']})
                        seen.add(record[pk])
        return result


def record_for(table, record_id, user, allow_published=True):
    pk, _ = TABLES[table]
    with engine.connect() as conn:
        row = conn.execute(text(f'SELECT * FROM public.{table} WHERE "{pk}"=:id' + ('' if user.is_admin else ' AND owner_id=:owner')), {'id': record_id, 'owner': user.id}).mappings().first()
        if row:
            return dict(row)
        if allow_published:
            for pub in snapshot_rows(conn, table):
                for item in pub['items'] or []:
                    if item[pk] == record_id:
                        return {k:v for k,v in item.items() if k != 'owner_id'}
    raise HTTPException(404, 'Record not found')


def own_record(conn, table, record_id, user):
    pk, _ = TABLES[table]
    row = conn.execute(text(f'SELECT * FROM public.{table} WHERE "{pk}"=:id' + ('' if user.is_admin else ' AND owner_id=:owner') + ' FOR UPDATE'), {'id': record_id, 'owner': user.id}).mappings().first()
    if not row:
        raise HTTPException(404, 'Record not found')
    return row


def clean_payload(conn, table, payload):
    pk, _ = TABLES[table]
    allowed = columns(conn, table)
    forbidden = {pk, 'owner_id', 'is_sota', 'read_only', 'sota_line_type'}
    unknown = set(payload) - set(allowed) - {'is_sota', 'read_only', 'sota_line_type'}
    if unknown:
        raise HTTPException(422, f'Unknown fields: {sorted(unknown)}')
    if 'owner_id' in payload or pk in payload:
        raise HTTPException(422, 'Owner and generated ID cannot be submitted')
    return {k: v for k, v in payload.items() if k in allowed and k not in forbidden}


def create(table, payload, user):
    pk, _ = TABLES[table]
    with engine.begin() as conn:
        values = clean_payload(conn, table, payload)
        values['owner_id'] = user.id
        keys = list(values)
        sql = f'INSERT INTO public.{table} (' + ', '.join(f'"{k}"' for k in keys) + ') VALUES (' + ', '.join(f':{k}' for k in keys) + f') RETURNING "{pk}"'
        record_id = conn.execute(text(sql), values).scalar_one()
    return {'status': 'created', pk: record_id}


def update(table, record_id, payload, user):
    pk, _ = TABLES[table]
    with engine.begin() as conn:
        own_record(conn, table, record_id, user)
        values = clean_payload(conn, table, payload)
        if not values:
            raise HTTPException(422, 'No editable fields')
        values['record_id'] = record_id
        assignments = ', '.join(f'"{k}"=:{k}' for k in values if k != 'record_id')
        conn.execute(text(f'UPDATE public.{table} SET {assignments} WHERE "{pk}"=:record_id'), values)
    return {'status': 'updated'}


def delete(table, record_id, user):
    pk, _ = TABLES[table]
    with engine.begin() as conn:
        own_record(conn, table, record_id, user)
        # Prevent breaking published scenarios, even for admin.
        for publication in snapshot_rows(conn, table):
            if any(item[pk] == record_id for item in publication['items'] or []):
                raise HTTPException(409, 'Record is used by a published SOTA; unpublish before deletion')
        conn.execute(text(f'DELETE FROM public.{table} WHERE "{pk}"=:id'), {'id': record_id})
    return {'status': 'deleted'}


def schema(table):
    with engine.connect() as conn:
        pk, _ = TABLES[table]
        return {'columns': [dict(v) for k,v in columns(conn,table).items() if k != 'owner_id']}


def options(table, user):
    pk, code = TABLES[table]
    if not code:
        raise HTTPException(404, 'No options')
    rows = visible_rows(table, user)
    return [r[code] for r in rows if r.get(code)]


def selectable_options(table, user):
    pk, code = TABLES[table]
    return [{'id': r[pk], 'code': r[code], 'is_sota': r['is_sota'], 'sota_line_type': r.get('sota_line_type')} for r in visible_rows(table,user) if r.get(code)]
