simulation.append({

    "technology_id": equipment["technology_id"],

    "technology_name": equipment["technology_name"],

    "process": equipment["process"],

    "category": category,

    "quality_rate": equipment["quality_rate"],

    "unit": unit,

    "required_output": round(output, 2),

    "required_input": round(input_required, 2),

    "operators_min": operators_min,

    "operators_max": operators_max,

    "machines": machines,

    "shifts": shifts_per_day,

    "uptime": round(uptime * 100, 2)

})

required_cells = required_input_cells

simulation.reverse()

return simulation