from fastapi import HTTPException
from sqlalchemy import text

from database import engine


# Fixed server-side table definitions. Never accept a table name
# or primary-key column from an HTTP request.
TABLES = {
    "equipment": ("equipment", "id"),
    "product": ("product_configuration", "row_id"),
    "material": ("product_material", "seq"),
    "plant": ("production_configuration", "id"),
}

# Fields the browser is never permitted to assign or modify.
PROTECTED_FIELDS = {
    "id",
    "row_id",
    "seq",
    "owner_id",
    "is_published",
    "published_at",
    "published_by",
}


def _table(kind):
    try:
        return TABLES[kind]
    except KeyError:
        raise HTTPException(500, "Invalid server-side record type")


def _writable_fields(conn, table, record):
    columns = set(
        conn.execute(
            text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = :table
                  AND is_generated = 'NEVER'
                  AND is_identity = 'NO'
            """),
            {"table": table},
        ).scalars()
    )

    forbidden = set(record) & PROTECTED_FIELDS
    if forbidden:
        raise HTTPException(
            400,
            f"These fields cannot be submitted: {', '.join(sorted(forbidden))}",
        )

    unknown = set(record) - columns
    if unknown:
        raise HTTPException(
            400,
            f"Unknown fields: {', '.join(sorted(unknown))}",
        )

    if not record:
        raise HTTPException(400, "No fields provided")

    return record


def list_private(kind, owner_id):
    table, primary_key = _table(kind)

    with engine.connect() as conn:
        rows = conn.execute(
            text(f"""
                SELECT *
                FROM public.{table}
                WHERE owner_id = :owner_id
                ORDER BY {primary_key}
            """),
            {"owner_id": owner_id},
        ).mappings().all()

    return [dict(row) for row in rows]


def get_private(kind, record_id, owner_id):
    table, primary_key = _table(kind)

    with engine.connect() as conn:
        row = conn.execute(
            text(f"""
                SELECT *
                FROM public.{table}
                WHERE {primary_key} = :record_id
                  AND owner_id = :owner_id
            """),
            {"record_id": record_id, "owner_id": owner_id},
        ).mappings().first()

    if row is None:
        raise HTTPException(404, "Record not found")

    return dict(row)


def create_private(kind, record, owner_id):
    table, primary_key = _table(kind)

    with engine.begin() as conn:
        values = _writable_fields(conn, table, record)
        values = {**values, "owner_id": owner_id}

        columns = ", ".join(f'"{key}"' for key in values)
        parameters = ", ".join(f":{key}" for key in values)

        row = conn.execute(
            text(f"""
                INSERT INTO public.{table} ({columns})
                VALUES ({parameters})
                RETURNING *
            """),
            values,
        ).mappings().one()

    return dict(row)


def update_private(kind, record_id, record, owner_id):
    table, primary_key = _table(kind)

    with engine.begin() as conn:
        values = _writable_fields(conn, table, record)

        set_clause = ", ".join(
            f'"{key}" = :value_{key}' for key in values
        )
        parameters = {
            f"value_{key}": value
            for key, value in values.items()
        }

        row = conn.execute(
            text(f"""
                UPDATE public.{table}
                SET {set_clause}
                WHERE {primary_key} = :record_id
                  AND owner_id = :owner_id
                RETURNING *
            """),
            {
                **parameters,
                "record_id": record_id,
                "owner_id": owner_id,
            },
        ).mappings().first()

    if row is None:
        raise HTTPException(404, "Record not found")

    return dict(row)


def delete_private(kind, record_id, owner_id):
    table, primary_key = _table(kind)

    with engine.begin() as conn:
        deleted_id = conn.execute(
            text(f"""
                DELETE FROM public.{table}
                WHERE {primary_key} = :record_id
                  AND owner_id = :owner_id
                RETURNING {primary_key}
            """),
            {
                "record_id": record_id,
                "owner_id": owner_id,
            },
        ).scalar_one_or_none()

    if deleted_id is None:
        raise HTTPException(404, "Record not found")

    return {"status": "deleted", "id": deleted_id}