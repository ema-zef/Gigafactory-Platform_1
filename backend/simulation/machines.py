import math

def calculate_machines(output_required, equipment, production):
    hours_per_shift = float(production["hours_per_shift"])
    shifts = int(production["no_of_shifts_per_day"])
    available_hours_year = float(production["available_time_min"])

    if hours_per_shift <= 0 or shifts <= 0 or available_hours_year <= 0:
        raise ValueError("Production time values must be greater than 0.")

    scheduled_hours_year = hours_per_shift * shifts * 365
    uptime = available_hours_year / scheduled_hours_year
    available_hours_day = available_hours_year / 365
    available_minutes_day = available_hours_day * 60

    category = (equipment["process_category"] or "").strip().upper()
    speed = equipment["speed_m_min"]
    processing_time = equipment["processingtime_min"]
    capacity = equipment["capacity"]

    if category in ("ROLL", "CATHODE_ROLL", "ANODE_ROLL"):
        if speed is None or float(speed) <= 0:
            raise ValueError(f"{equipment['technology_name']} has invalid speed_m_min: {speed}")
        daily_capacity = float(speed) * available_minutes_day
        batches = None
    else:
        if processing_time is None or float(processing_time) <= 0:
            raise ValueError(f"{equipment['technology_name']} has invalid processingtime_min: {processing_time}")
        if capacity is None or float(capacity) <= 0:
            raise ValueError(f"{equipment['technology_name']} has invalid capacity: {capacity}")
        processing_time = float(processing_time)
        capacity = float(capacity)
        daily_capacity = available_minutes_day * capacity / processing_time
        batches = math.ceil(available_minutes_day / processing_time) if category in ("MASS", "CATHODE_MASS", "ANODE_MASS") else None

    if daily_capacity <= 0:
        raise ValueError(f"Calculated daily capacity is {daily_capacity} for {equipment['technology_name']}.")

    machine_count = math.ceil(float(output_required) / daily_capacity)

    return {
        "machines": machine_count,
        "batches": batches,
        "shifts": shifts,
        "uptime": round(uptime, 6),
        "available_hours_year": available_hours_year,
        "available_hours_day": round(available_hours_day, 6),
        "daily_capacity_per_machine": daily_capacity,
    }
