def calculate_costs(machines, operators, energy, equipment, production):
    electricity_price = float(production["electricity_price_eur_kwh"] or 0)
    gas_price = float(production["gas_price_eur_kwh"] or 0)
    labour_rate = float(production["labour_cost_eur_hour"] or 0)

    available_hours_year = float(production["available_time_min"])
    operating_hours_day = available_hours_year / 365
    operator_count = float(operators["operators_min"] or 0)

    electricity_cost = energy["electricity"] * electricity_price
    gas_cost = energy["gas"] * gas_price
    labour_cost = operator_count * operating_hours_day * labour_rate

    direct_operating_cost = labour_cost + electricity_cost + gas_cost
    overhead_percentage = float(production["Cost_Overhead_Factor_(%)"] or 0)
    overhead_cost = direct_operating_cost * overhead_percentage / 100
    total = direct_operating_cost + overhead_cost

    return {
        "labour": round(labour_cost, 2),
        "electricity": round(electricity_cost, 2),
        "gas": round(gas_cost, 2),
        "overhead": round(overhead_cost, 2),
        "direct_operating": round(direct_operating_cost, 2),
        "total": round(total, 2),
    }
