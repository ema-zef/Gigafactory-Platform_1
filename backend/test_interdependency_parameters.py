from fastapi import HTTPException

from interdependency_parameters import (
    default_eligibility,
    effective_eligibility,
    validate_eligibility,
)

TABLE = "product_configuration"
COLUMNS = [
    "row_id",
    "plantcode",
    "submitted_by",
    "type",
    "cell_capacity_kwh",
    "interdependency_parameters",
]

expected = {
    "cell_capacity_kwh": True,
    "type": True,
}

assert default_eligibility(TABLE, COLUMNS) == expected

assert validate_eligibility(
    TABLE, COLUMNS, {"type": False}
) == {
    "cell_capacity_kwh": True,
    "type": False,
}

assert effective_eligibility(
    TABLE,
    COLUMNS,
    {"type": False, "plantcode": True},
) == {
    "cell_capacity_kwh": True,
    "type": False,
}

for invalid in [
    {"plantcode": True},
    {"type": "false"},
    {"type": 1},
]:
    try:
        validate_eligibility(TABLE, COLUMNS, invalid)
    except HTTPException as error:
        assert error.status_code == 422
    else:
        raise AssertionError(f"Invalid flags accepted: {invalid}")

print("PASS: Interdependency eligibility validation")