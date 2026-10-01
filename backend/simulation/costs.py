def calculate_costs(
    machines,
    operators,
    energy,
    equipment,
    production
):
    # ----------------------------------
    # Production cost rates
    # ----------------------------------

    electricity_price = float(
        production[
            "electricity_cost_rate_min_eur_per_kwh"
        ] or 0
    )

    gas_price = float(
        production[
            "gas_cost_rate_min_eur_per_kwh"
        ] or 0
    )

    labour_rate = float(
        production["operator_rate"] or 0
    )

    overhead_percentage = float(
        production["Cost_Overhead_Factor_(%)"] or 0
    )

    floor_space_rate = float(
        production["floor_space_cost_rate_eur_per_m2"] or 0
    )

    # Legacy DB name:
    # available_time_min actually contains
    # annual available HOURS.
    available_hours_year = float(
        production["available_time_min"]
    )

    operating_hours_day = (
        available_hours_year / 365
    )

    operator_count = float(
        operators["operators_min"] or 0
    )

    # ----------------------------------
    # Energy costs - EUR/day
    # ----------------------------------

    electricity_cost = (
        energy["electricity"]
        * electricity_price
    )

    gas_cost = (
        energy["gas"]
        * gas_price
    )

    # ----------------------------------
    # Labour cost - EUR/day
    # ----------------------------------

    labour_cost = (
        operator_count
        * operating_hours_day
        * labour_rate
    )

    # ----------------------------------
    # Direct operating cost
    # ----------------------------------

    direct_operating_cost = (
        labour_cost
        + electricity_cost
        + gas_cost
    )

    # ----------------------------------
    # Overhead - EUR/day
    # ----------------------------------
    overhead_cost = (
        direct_operating_cost
        * overhead_percentage
        / 100
    )

    # ----------------------------------
    # Floor-space cost - EUR/day
    # ----------------------------------
    # Rate: EUR/m2/hour.
    machine_count = float(machines["machines"] or 0)
    equipment_floor_space_m2 = float(
        equipment["equipment_floor_space_m_2"] or 0
    )
    total_machine_floor_space_m2 = (
        machine_count * equipment_floor_space_m2
    )
    floor_space_cost = (
        total_machine_floor_space_m2
        * floor_space_rate
        * operating_hours_day
    )

    total = (
        direct_operating_cost
        + overhead_cost
        + floor_space_cost
    )

    return {
        "labour": round(
            labour_cost, 2
        ),

        "electricity": round(
            electricity_cost, 2
        ),

        "gas": round(
            gas_cost, 2
        ),

        "overhead": round(
            overhead_cost, 2
        ),

        "floor_space": round(
            floor_space_cost, 2
        ),

        "floor_space_m2": round(
            total_machine_floor_space_m2, 4
        ),

        "floor_space_rate_eur_per_m2_h": round(
            floor_space_rate, 6
        ),

        "overhead_percentage": round(
            overhead_percentage, 4
        ),

        "direct_operating": round(
            direct_operating_cost, 2
        ),

        "total": round(
            total, 2
        )
    }