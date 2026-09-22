ddef calculate_costs(
    machines,
    operators,
    energy,
    equipment,
    production
):

    machine_count = machines["machines"]

    electricity_price = float(
        production["electricity_price_eur_kwh"]
        or 0
    )

    gas_price = float(
        production["gas_price_eur_kwh"]
        or 0
    )

    labour_rate = float(
        production["labour_cost_eur_hour"]
        or 0
    )

    hours_per_shift = float(
        production["hours_per_shift"]
    )

    shifts = int(
        production["no_of_shifts_per_day"]
    )

    operator_count = operators["operators_min"]

    # -------------------------
    # Energy cost
    # -------------------------

    electricity_cost = (
        energy["electricity"]
        * electricity_price
    )

    gas_cost = (
        energy["gas"]
        * gas_price
    )

    # -------------------------
    # Labour cost
    # -------------------------

    labour_cost = (
        operator_count
        * hours_per_shift
        * shifts
        * labour_rate
    )

    # -------------------------
    # Total
    # -------------------------

    total = (
        electricity_cost
        + gas_cost
        + labour_cost
    )

    return {
        "labour": round(labour_cost, 2),
        "electricity": round(electricity_cost, 2),
        "gas": round(gas_cost, 2),
        "total": round(total, 2)
    }