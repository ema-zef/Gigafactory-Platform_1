"""Authenticated, owner-scoped product configuration routes.

Private records remain private for administrators too. Published SOTA access is
intentionally not implemented here; it requires a separate explicit policy.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from auth import User, current_user
from database import (
    engine,
    product_configuration_schema as get_product_configuration_schema,
    check_product_configuration,
)

router = APIRouter(dependencies=[Depends(current_user)])

# Existing React forms may submit the primary key when copying/editing records.
# It is ignored on create, but ownership and publication fields are rejected.
PRIMARY_KEY_FIELDS = {"id", "row_id", "seq"}
PROTECTED_FIELDS = {
    "owner_id", "is_published", "published_at", "published_by"
}


def _validated_product_fields(conn, record: dict, *, creating: bool) -> dict:
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
          AND table_name = 'product_configuration'
          AND is_generated = 'NEVER'
          AND is_identity = 'NO'
    """)).scalars().all()) - PRIMARY_KEY_FIELDS - PROTECTED_FIELDS

    unknown = set(record) - allowed
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown product fields: {', '.join(sorted(unknown))}",
        )
    if not record:
        raise HTTPException(status_code=400, detail="No product fields provided")

    if "productcode" in record:
        if record["productcode"] is None or not str(record["productcode"]).strip():
            raise HTTPException(status_code=422, detail="Product code is required")
        record["productcode"] = str(record["productcode"]).strip()
    elif creating:
        raise HTTPException(status_code=422, detail="Product code is required")

    return record


@router.post("/product_configuration")
def create_product(record: dict, user: User = Depends(current_user)):
    try:
        with engine.begin() as conn:
            values = _validated_product_fields(conn, record, creating=True)
            values = {**values, "owner_id": user.id}
            columns = ", ".join(f'"{column}"' for column in values)
            placeholders = ", ".join(f":{column}" for column in values)
            row_id = conn.execute(
                text(f"""
                    INSERT INTO public.product_configuration ({columns})
                    VALUES ({placeholders})
                    RETURNING row_id
                """),
                values,
            ).scalar_one()
    except IntegrityError as exc:
        if getattr(exc.orig, "diag", None) and exc.orig.diag.constraint_name == "uq_product_configuration_owner_productcode":
            raise HTTPException(status_code=409, detail="You already have a product with this product code") from exc
        raise

    return {
        "status": "created",
        "id": row_id,
        "productcode": values["productcode"],
        "material_required": True,
    }


@router.get("/product_configuration")
def get_products(user: User = Depends(current_user)):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT * FROM public.product_configuration
            WHERE owner_id = :owner_id
            ORDER BY row_id
        """), {"owner_id": user.id}).mappings().all()
    return [dict(row) for row in rows]


@router.get("/product_configuration/options")
def product_options(user: User = Depends(current_user)):
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT pc.productcode
            FROM public.product_configuration pc
            WHERE pc.owner_id = :owner_id
              AND pc.productcode IS NOT NULL
              AND EXISTS (
                  SELECT 1
                  FROM public.product_material pm
                  WHERE pm.owner_id = pc.owner_id
                    AND pm.productcode = pc.productcode
              )
            ORDER BY pc.productcode
        """), {"owner_id": user.id}).scalars().all()


@router.get("/product_configuration/schema")
def product_schema():
    return get_product_configuration_schema()


@router.get("/product_configuration/check")
def product_check():
    return check_product_configuration()


@router.get("/product_configuration/{record_id}")
def get_product(record_id: int, user: User = Depends(current_user)):
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT * FROM public.product_configuration
            WHERE row_id = :record_id AND owner_id = :owner_id
        """), {"record_id": record_id, "owner_id": user.id}).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)


@router.put("/product_configuration/{record_id}")
def update_product(
    record_id: int,
    record: dict,
    user: User = Depends(current_user),
):
    try:
        with engine.begin() as conn:
            values = _validated_product_fields(conn, record, creating=False)
            set_clause = ", ".join(f'"{column}" = :value_{column}' for column in values)
            params = {f"value_{column}": value for column, value in values.items()}
            updated_id = conn.execute(text(f"""
                UPDATE public.product_configuration
                SET {set_clause}
                WHERE row_id = :record_id AND owner_id = :owner_id
                RETURNING row_id
            """), {**params, "record_id": record_id, "owner_id": user.id}).scalar_one_or_none()
    except IntegrityError as exc:
        if getattr(exc.orig, "diag", None) and exc.orig.diag.constraint_name == "uq_product_configuration_owner_productcode":
            raise HTTPException(status_code=409, detail="You already have a product with this product code") from exc
        raise
    if updated_id is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "updated"}


@router.delete("/product_configuration/{record_id}")
def delete_product(record_id: int, user: User = Depends(current_user)):
    with engine.begin() as conn:
        deleted_id = conn.execute(text("""
            DELETE FROM public.product_configuration
            WHERE row_id = :record_id AND owner_id = :owner_id
            RETURNING row_id
        """), {"record_id": record_id, "owner_id": user.id}).scalar_one_or_none()
    if deleted_id is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "deleted"}
