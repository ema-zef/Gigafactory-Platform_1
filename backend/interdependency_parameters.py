
from fastapi import HTTPException

ELIGIBILITY_TABLES = frozenset({
    "equipment",
    "product_configuration",
    "production_configuration",
})

EXCLUDED_FIELDS = frozenset({
    "id",
    "row_id",
    "seq",
    "owner_id",
    "created_at",
    "updated_at",
    "is_sota",
    "read_only",
    "sota_line_type",
    "interdependency_parameters",
    "productcode",
    "code",
    "plantcode",
    "submitted_by",
    "submitted_on",
})


def eligible_parameter_names(table, column_names):
    if table not in ELIGIBILITY_TABLES:
        return []

    return sorted(
        name for name in column_names
        if name not in EXCLUDED_FIELDS
    )


def default_eligibility(table, column_names):
    return {
        name: True
        for name in eligible_parameter_names(table, column_names)
    }


def validate_eligibility(table, column_names, value):
    if table not in ELIGIBILITY_TABLES:
        raise HTTPException(
            422,
            "Interdependency eligibility is not supported for this table",
        )

    if not isinstance(value, dict):
        raise HTTPException(
            422,
            "Interdependency parameters must be a JSON object",
        )

    allowed = set(eligible_parameter_names(table, column_names))
    unknown = set(value) - allowed

    if unknown:
        raise HTTPException(
            422,
            f"Unknown interdependency parameters: {sorted(unknown)}",
        )

    if any(type(flag) is not bool for flag in value.values()):
        raise HTTPException(
            422,
            "Interdependency parameter flags must be Boolean",
        )

    result = default_eligibility(table, column_names)
    result.update(value)
    return result


def effective_eligibility(table, column_names, stored_value):
    if not isinstance(stored_value, dict):
        stored_value = {}

    allowed = set(eligible_parameter_names(table, column_names))
    result = default_eligibility(table, column_names)

    for name, flag in stored_value.items():
        if name in allowed and type(flag) is bool:
            result[name] = flag

    return result
