"""Shared controlled-environment infrastructure calculation.

Environment energy/cost/carbon is calculated once per environment type and is
then allocated back to assigned technologies by attributable controlled area.
Allocated values are analytical only; factory totals use the environment total
once, preventing double counting.
"""

ENVIRONMENT_TYPES = ("dry_room", "glove_box", "mini_environment")


def _f(value):
    return float(value or 0)


def calculate_environment(environment_type, config, assignments, production):
    if environment_type not in ENVIRONMENT_TYPES:
        raise ValueError(f"Unsupported environment type: {environment_type}")

    operating_hours_day = _f(production["available_time_min"]) / 365.0
    area_factor = _f(config.get("area_factor"))
    fixed_area_m2 = _f(config.get("fixed_area_m2"))

    base_area_m2 = sum(_f(item.get("equipment_footprint_m2")) for item in assignments)
    controlled_area_m2 = base_area_m2 * area_factor + fixed_area_m2

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

    electricity_cost = electricity * _f(production["electricity_cost_rate_min_eur_per_kwh"])
    gas_cost = gas * _f(production["gas_cost_rate_min_eur_per_kwh"])
    labour = _f(config.get("operator_count")) * operating_hours_day * _f(production["operator_rate"])
    maintenance = _f(config.get("maintenance_cost_eur_day"))

    direct_operating = electricity_cost + gas_cost + labour + maintenance
    overhead = direct_operating * _f(production["Cost_Overhead_Factor_(%)"]) / 100.0

    # Controlled environment itself occupies factory floor area.
    floor_space = (
        controlled_area_m2
        * _f(production["floor_space_cost_rate_eur_per_m2"])
        * operating_hours_day
    )

    total_cost = direct_operating + overhead + floor_space
    electricity_carbon = electricity * _f(production["elec_ghge_rate"])
    gas_carbon = gas * _f(production["gas_ghge_rate"])
    total_carbon = electricity_carbon + gas_carbon

    # Fixed room area is shared in proportion to equipment footprint.
    denominator = base_area_m2
    if denominator <= 0 and assignments:
        denominator = float(len(assignments))

    allocations = []
    for item in assignments:
        if base_area_m2 > 0:
            share = _f(item.get("equipment_footprint_m2")) / base_area_m2
        else:
            share = 1.0 / len(assignments) if assignments else 0

        allocations.append({
            "technology_id": item["technology_id"],
            "technology_name": item["technology_name"],
            "branch": item.get("branch"),
            "share": round(share, 8),
            "controlled_area_m2": round(controlled_area_m2 * share, 4),
            "energy": {
                "electricity": round(electricity * share, 2),
                "gas": round(gas * share, 2),
                "total": round((electricity + gas) * share, 2),
            },
            "costs": {
                "total": round(total_cost * share, 2),
            },
            "carbon": {
                "total": round(total_carbon * share, 2),
            },
        })

    return {
        "environment_type": environment_type,
        "code": config.get("code"),
        "name": config.get("name"),
        "assigned_processes": len(assignments),
        "base_equipment_footprint_m2": round(base_area_m2, 4),
        "controlled_area_m2": round(controlled_area_m2, 4),
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
