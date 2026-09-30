"""Authenticated, owner-scoped product material routes.

Each private product can have exactly one material record. Product ownership is
always derived from the authenticated user, never from the request body.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from auth import User, current_user
from database import engine, get_product_material_schema, check_product_material

router = APIRouter(dependencies=[Depends(current_user)])

PRIMARY_KEY_FIELDS = {"id", "row_id", "seq"}
PROTECTED_FIELDS = {"owner_id", "is_published", "published_at", "published_by"}


def _validated_material_fields(conn, record: dict, *, creating: bool) -> dict:
    if not isinstance(record, dict):
        raise HTTPException(status_code=422, detail="Expected a JSON object")

    forbidden = PROTECTED_FIELDS.intersection(record)
    if forbidden:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot set protected fields: {', '.join(sorted(forbidden))}",
        )

    if creating:
        record = {k: v for k, v in record.items() if k not in PRIMARY_KEY_FIELDS}
    elif PRIMARY_KEY_FIELDS.intersection(record):
        raise HTTPException(status_code=400, detail="Cannot update primary key")

    allowed = set(conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'product_material'
          AND is_generated = 'NEVER'
          AND is_identity = 'NO'
    """)).scalars().all()) - PRIMARY_KEY_FIELDS - PROTECTED_FIELDS

    unknown = set(record) - allowed
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown product material fields: {', '.join(sorted(unknown))}",
        )
    if not record:
        raise HTTPException(status_code=400, detail="No product material fields provided")

    if "productcode" in record:
        if record["productcode"] is None or not str(record["productcode"]).strip():
            raise HTTPException(status_code=422, detail="Product code is required")
        record["productcode"] = str(record["productcode"]).strip()
    elif creating:
        raise HTTPException(status_code=422, detail="Product code is required")

    return record


def _require_owned_product(conn, owner_id: str, productcode: str) -> None:
    exists = conn.execute(text("""
        SELECT 1
        FROM public.product_configuration
        WHERE owner_id = :owner_id
          AND productcode = :productcode
    """), {"owner_id": owner_id, "productcode": productcode}).scalar_one_or_none()
    if exists is None:
        raise HTTPException(status_code=404, detail="Product not found or not accessible")


@router.post("/product_material")
def create_product_material(record: dict, user: User = Depends(current_user)):
    try:
        with engine.begin() as conn:
            values = _validated_material_fields(conn, record, creating=True)
            _require_owned_product(conn, user.id, values["productcode"])
            values = {**values, "owner_id": user.id}
            columns = ", ".join(f'"{column}"' for column in values)
            placeholders = ", ".join(f":{column}" for column in values)
            seq = conn.execute(text(f"""
                INSERT INTO public.product_material ({columns})
                VALUES ({placeholders})
                RETURNING seq
            """), values).scalar_one()
    except IntegrityError as exc:
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint == "uq_product_material_owner_productcode":
            raise HTTPException(status_code=409, detail="This product already has a material record") from exc
        if constraint == "fk_product_material_owner_product":
            raise HTTPException(status_code=404, detail="Product not found or not accessible") from exc
        raise

    return {"status": "created", "id": seq, "productcode": values["productcode"]}


@router.get("/product_material")
def get_product_material(user: User = Depends(current_user)):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT * FROM public.product_material
            WHERE owner_id = :owner_id
            ORDER BY seq
        """), {"owner_id": user.id}).mappings().all()
    return [dict(row) for row in rows]


@router.get("/product_material/options")
def get_product_material_options(user: User = Depends(current_user)):
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT productcode
            FROM public.product_material
            WHERE owner_id = :owner_id
            ORDER BY productcode
        """), {"owner_id": user.id}).scalars().all()


@router.get("/product_material/schema")
def product_material_schema():
    return get_product_material_schema()


@router.get("/product_material/check")
def product_material_check():
    return check_product_material()


@router.get("/product_material/{record_id}")
def get_product_material_record(record_id: int, user: User = Depends(current_user)):
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT * FROM public.product_material
            WHERE seq = :record_id AND owner_id = :owner_id
        """), {"record_id": record_id, "owner_id": user.id}).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Product material not found")
    return dict(row)


@router.put("/product_material/{record_id}")
def update_product_material(record_id: int, record: dict, user: User = Depends(current_user)):
    try:
        with engine.begin() as conn:
            values = _validated_material_fields(conn, record, creating=False)

            current = conn.execute(text("""
                SELECT productcode
                FROM public.product_material
                WHERE seq = :record_id AND owner_id = :owner_id
            """), {"record_id": record_id, "owner_id": user.id}).mappings().first()
            if current is None:
                raise HTTPException(status_code=404, detail="Product material not found")

            if "productcode" in values:
                _require_owned_product(conn, user.id, values["productcode"])

            set_clause = ", ".join(f'"{column}" = :value_{column}' for column in values)
            params = {f"value_{column}": value for column, value in values.items()}
            conn.execute(text(f"""
                UPDATE public.product_material
                SET {set_clause}
                WHERE seq = :record_id AND owner_id = :owner_id
            """), {**params, "record_id": record_id, "owner_id": user.id})
    except IntegrityError as exc:
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint == "uq_product_material_owner_productcode":
            raise HTTPException(status_code=409, detail="This product already has a material record") from exc
        if constraint == "fk_product_material_owner_product":
            raise HTTPException(status_code=404, detail="Product not found or not accessible") from exc
        raise

    return {"status": "updated"}


@router.delete("/product_material/{record_id}")
def delete_product_material(record_id: int, user: User = Depends(current_user)):
    with engine.begin() as conn:
        deleted = conn.execute(text("""
            DELETE FROM public.product_material
            WHERE seq = :record_id AND owner_id = :owner_id
            RETURNING seq
        """), {"record_id": record_id, "owner_id": user.id}).scalar_one_or_none()
    if deleted is None:
        raise HTTPException(status_code=404, detail="Product material not found")
    return {"status": "deleted"}
