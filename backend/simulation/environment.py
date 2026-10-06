"""Shared controlled-environment infrastructure calculation.

For a Dry Room, required controlled area is derived from the total machine
footprint assigned to the room multiplied by the configured area factor.
The design area is a capacity/reference limit, not the automatically charged
simulation area.

Environment totals are counted once at factory level and allocated back to
assigned technologies by attributable machine footprint for analytics.
"""

ENVIRONMENT_TYPES = ("dry_room", "glove_box", "mini_environment")


def _f(value):
    return float(value or 0)


def calculate_environment(environment_type, config, assignments, production):
    if environment_type not in ENVIRONMENT_TYPES:
        raise ValueError(f"Unsupported environment type: {environment_type}")

    if not assignments:
        raise ValueError(
            f"{environment_type} was requested without any assigned technologies"
        )

    operating_hours_day = _f(production["available_time_min"]) / 365.0
    area_factor = _f(config.get("area_factor"))
    fixed_area_m2 = _f(config.get("fixed_area_m2"))

    base_area_m2 = sum(
        _f(item.get("equipment_footprint_m2"))
        for item in assignments
    )

    # Do not invent an equal process split when footprint data is missing.
    if base_area_m2 <= 0:
        raise ValueError(
            f"{config.get('code') or environment_type} cannot be calculated "
            "because the assigned equipment has no attributable machine footprint."
        )

    controlled_area_m2 = base_area_m2 * area_factor + fixed_area_m2

    design_area_m2 = _f(config.get("design_area_m2"))
    capacity_exceeded = (
        design_area_m2 > 0
        and controlled_area_m2 > design_area_m2
    )
    capacity_utilization_pct = (
        controlled_area_m2 / design_area_m2 * 100.0
        if design_area_m2 > 0
        else None
    )

    electricity = (
        controlled_area_m2
        * _f(config.get("electricity_kwh_per_m2_h"))
        * operating_hours_day
        + _f(config.get("fixed_electricity_kwh_day"))
    )
    gas = (
        controlled_area_m2
        * _f(config.get("gas_kwh_per_m2_h"))
        * operating_hours_day
        + _f(config.get("fixed_gas_kwh_day"))
    )

    electricity_cost = (
        electricity
        * _f(production["electricity_cost_rate_min_eur_per_kwh"])
    )
    gas_cost = (
        gas
        * _f(production["gas_cost_rate_min_eur_per_kwh"])
    )
    labour = (
        _f(config.get("operator_count"))
        * operating_hours_day
        * _f(production["operator_rate"])
    )
    maintenance = _f(config.get("maintenance_cost_eur_day"))

    # Keep the established overhead basis: labour + electricity + gas.
    overhead_base = electricity_cost + gas_cost + labour
    overhead = (
        overhead_base
        * _f(production["Cost_Overhead_Factor_(%)"])
        / 100.0
    )

    direct_operating = overhead_base + maintenance

    # The equipment calculator already charges the base machine footprint.
    # Environment floor-space cost therefore charges only the incremental
    # allowance/fixed area needed by the controlled environment.
    incremental_environment_area_m2 = max(
        controlled_area_m2 - base_area_m2,
        0.0,
    )
    floor_space = (
        incremental_environment_area_m2
        * _f(production["floor_space_cost_rate_eur_per_m2"])
        * operating_hours_day
    )

    total_cost = direct_operating + overhead + floor_space

    electricity_carbon = (
        electricity * _f(production["elec_ghge_rate"])
    )
    gas_carbon = gas * _f(production["gas_ghge_rate"])
    total_carbon = electricity_carbon + gas_carbon

    allocations = []
    for assignment_index, item in enumerate(assignments):
        share = (
            _f(item.get("equipment_footprint_m2"))
            / base_area_m2
        )

        allocations.append({
            "assignment_index": assignment_index,
            "technology_id": item["technology_id"],
            "technology_name": item["technology_name"],
            "branch": item.get("branch"),
            "share": round(share, 8),
            "base_equipment_footprint_m2": round(
                _f(item.get("equipment_footprint_m2")),
                4,
            ),
            "controlled_area_m2": round(
                controlled_area_m2 * share,
                4,
            ),
            "energy": {
                "electricity": round(electricity * share, 2),
                "gas": round(gas * share, 2),
                "total": round((electricity + gas) * share, 2),
            },
            "costs": {
                "electricity": round(electricity_cost * share, 2),
                "gas": round(gas_cost * share, 2),
                "labour": round(labour * share, 2),
                "maintenance": round(maintenance * share, 2),
                "overhead": round(overhead * share, 2),
                "floor_space": round(floor_space * share, 2),
                "total": round(total_cost * share, 2),
            },
            "carbon": {
                "electricity": round(electricity_carbon * share, 2),
                "gas": round(gas_carbon * share, 2),
                "total": round(total_carbon * share, 2),
            },
        })

    result = {
        "environment_type": environment_type,
        "code": config.get("code"),
        "name": config.get("name"),
        "assigned_processes": len(assignments),
        "operating_hours_day": round(operating_hours_day, 4),
        "area_factor": round(area_factor, 6),
        "base_equipment_footprint_m2": round(base_area_m2, 4),
        "controlled_area_m2": round(controlled_area_m2, 4),
        "incremental_environment_area_m2": round(
            incremental_environment_area_m2,
            4,
        ),
        "design_area_m2": (
            round(design_area_m2, 4)
            if design_area_m2 > 0
            else None
        ),
        "capacity_utilization_pct": (
            round(capacity_utilization_pct, 2)
            if capacity_utilization_pct is not None
            else None
        ),
        "capacity_exceeded": capacity_exceeded,
        "purchase_installation_cost_eur": round(
            _f(config.get("purchase_installation_cost_eur")),
            2,
        ),
        "energy": {
            "electricity": round(electricity, 2),
            "gas": round(gas, 2),
            "total": round(electricity + gas, 2),
        },
        "costs": {
            "labour": round(labour, 2),
            "electricity": round(electricity_cost, 2),
            "gas": round(gas_cost, 2),
            "maintenance": round(maintenance, 2),
            "overhead": round(overhead, 2),
            "floor_space": round(floor_space, 2),
            "direct_operating": round(direct_operating, 2),
            "total": round(total_cost, 2),
        },
        "carbon": {
            "electricity": round(electricity_carbon, 2),
            "gas": round(gas_carbon, 2),
            "total": round(total_carbon, 2),
        },
        "allocations": allocations,
    }

    if capacity_exceeded:
        result["capacity_warning"] = (
            f"{config.get('code') or environment_type} requires "
            f"{controlled_area_m2:.2f} m², exceeding its "
            f"{design_area_m2:.2f} m² design area."
        )

    return result
