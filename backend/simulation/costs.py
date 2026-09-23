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
    # Overhead
    # ----------------------------------
    # Not currently returned by
    # production_configuration.
    # Keep at zero until the DB field is
    # added/loaded.

    overhead_percentage = 0.0

    overhead_cost = (
        direct_operating_cost
        * overhead_percentage
        / 100
    )

    total = (
        direct_operating_cost
        + overhead_cost
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

        "direct_operating": round(
            direct_operating_cost, 2
        ),

        "total": round(
            total, 2
        )
    }