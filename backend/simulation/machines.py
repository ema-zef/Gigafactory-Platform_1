import math


def calculate_machines(output_required, equipment, production):
    hours_per_shift = float(production["hours_per_shift"])
    shifts = int(production["no_of_shifts_per_day"])

    # Legacy DB name: available_time_min actually stores HOURS/year.
    available_hours_year = float(production["available_time_min"])

    if hours_per_shift <= 0:
        raise ValueError("hours_per_shift must be greater than 0.")
    if shifts <= 0:
        raise ValueError("no_of_shifts_per_day must be greater than 0.")
    if available_hours_year <= 0:
        raise ValueError("available annual hours must be greater than 0.")

    scheduled_hours_year = hours_per_shift * shifts * 365
    uptime = available_hours_year / scheduled_hours_year

    # Material-flow requirements are expressed per day.
    available_hours_day = available_hours_year / 365
    available_minutes_day = available_hours_day * 60

    technology_name = equipment["technology_name"] or "Unknown technology"
    category = (equipment["process_category"] or "").strip().upper()

    speed = equipment["speed_m_min"]
    processing_time = equipment["processingtime_min"]
    capacity = equipment["capacity"]

    speed = float(speed) if speed is not None else None
    processing_time = float(processing_time) if processing_time is not None else None
    capacity = float(capacity) if capacity is not None else None

    capacity_method = None
    batches = None

    if category in ("ROLL", "CATHODE_ROLL", "ANODE_ROLL"):
        # Preferred for continuous web equipment: m/min * min/day = m/day.
        if speed is not None and speed > 0:
            daily_capacity = speed * available_minutes_day
            capacity_method = "speed"

        # Some ROLL equipment (e.g. dryers) has no speed but has a stored
        # daily capacity. Use it rather than rejecting the technology.
        elif capacity is not None and capacity > 0:
            daily_capacity = capacity
            capacity_method = "stored_capacity"

        else:
            raise ValueError(
                f"{technology_name} has insufficient ROLL capacity data: "
                f"speed_m_min={speed}, capacity={capacity}."
            )

    else:
        # Cycle-based capacity when both cycle time and capacity/cycle exist.
        if (
            processing_time is not None
            and processing_time > 0
            and capacity is not None
            and capacity > 0
        ):
            daily_capacity = (
                available_minutes_day * capacity / processing_time
            )
            capacity_method = "cycle"

        # If cycle time is absent, use a valid stored capacity directly.
        elif capacity is not None and capacity > 0:
            daily_capacity = capacity
            capacity_method = "stored_capacity"

        else:
            raise ValueError(
                f"{technology_name} has insufficient capacity data: "
                f"processingtime_min={processing_time}, capacity={capacity}."
            )

        # MASS equipment is treated as batch equipment when cycle time exists.
        if (
            category in ("MASS", "CATHODE_MASS", "ANODE_MASS")
            and processing_time is not None
            and processing_time > 0
        ):
            batches = math.ceil(available_minutes_day / processing_time)

    if daily_capacity <= 0:
        raise ValueError(
            f"Calculated daily capacity is {daily_capacity} for {technology_name}."
        )

    required_output = float(output_required)
    if required_output < 0:
        raise ValueError(
            f"output_required cannot be negative for {technology_name}: "
            f"{required_output}"
        )

    machine_count = math.ceil(required_output / daily_capacity)

    return {
        "machines": machine_count,
        "batches": batches,
        "shifts": shifts,
        "uptime": round(uptime, 6),
        "available_hours_year": round(available_hours_year, 6),
        "available_hours_day": round(available_hours_day, 6),
        "available_minutes_day": round(available_minutes_day, 6),
        "daily_capacity_per_machine": round(daily_capacity, 6),
        "capacity_method": capacity_method,
    }

