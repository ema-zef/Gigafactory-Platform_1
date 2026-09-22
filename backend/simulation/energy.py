def calculate_energy(
    machines,
    equipment,
    production
):

    machine_count = int(machines["machines"])

    if machine_count <= 0:
        return {
            "electricity": 0,
            "gas": 0,
            "total": 0,
            "per_machine": {
                "electricity": 0,
                "gas": 0,
                "total": 0,
            }
        }

    available_minutes = float(
        production["available_time_min"]
    )

    if available_minutes <= 0:
        raise ValueError(
            f"Invalid available_time_min: {available_minutes}"
        )

    operating_hours = available_minutes / 60

    electricity_value = (
        equipment[
            "electricity_consumption_kwhcell_kwh_min"
        ]
        or 0
    )

    gas_value = (
        equipment[
            "natural_gas_energy_consumption_of_kw_min"
        ]
        or 0
    )

    electricity_kw = float(electricity_value)
    gas_kw = float(gas_value)

    electricity = (
        electricity_kw
        * operating_hours
        * machine_count
    )

    gas = (
        gas_kw
        * operating_hours
        * machine_count
    )

    total = electricity + gas

    return {
        "electricity": round(electricity, 2),
        "gas": round(gas, 2),
        "total": round(total, 2),

        "per_machine": {
            "electricity": round(
                electricity / machine_count, 2
            ),
            "gas": round(
                gas / machine_count, 2
            ),
            "total": round(
                total / machine_count, 2
            ),
        }
    }