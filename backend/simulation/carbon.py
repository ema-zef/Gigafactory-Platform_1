def calculate_carbon(
    energy,
    production
):

    electricity_factor = float(
        production["electricity_kgco2e_kwh"]
        or 0
    )

    gas_factor = float(
        production["gas_kgco2e_kwh"]
        or 0
    )

    electricity_carbon = (
        energy["electricity"]
        * electricity_factor
    )

    gas_carbon = (
        energy["gas"]
        * gas_factor
    )

    total = (
        electricity_carbon
        + gas_carbon
    )

    return {
        "electricity": round(
            electricity_carbon, 2
        ),
        "gas": round(
            gas_carbon, 2
        ),
        "total": round(
            total, 2
        )
    }