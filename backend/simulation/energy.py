def calculate_energy(machines, equipment, production):
    machine_count = int(machines["machines"])
    if machine_count <= 0:
        return {"electricity": 0, "gas": 0, "total": 0,
                "per_machine": {"electricity": 0, "gas": 0, "total": 0}}

    available_hours_year = float(production["available_time_min"])
    if available_hours_year <= 0:
        raise ValueError(f"Invalid annual available hours: {available_hours_year}")

    operating_hours_day = available_hours_year / 365

    electricity_kw = float(equipment["electricity_consumption_kwhcell_kwh_min"] or 0)
    gas_kw = float(equipment["natural_gas_energy_consumption_of_kw_min"] or 0)

    # Assumption: both equipment values are average power in kW.
    electricity = electricity_kw * operating_hours_day * machine_count
    gas = gas_kw * operating_hours_day * machine_count
    total = electricity + gas

    return {
        "electricity": round(electricity, 2),
        "gas": round(gas, 2),
        "total": round(total, 2),
        "per_machine": {
            "electricity": round(electricity / machine_count, 2),
            "gas": round(gas / machine_count, 2),
            "total": round(total / machine_count, 2),
        },
    }
