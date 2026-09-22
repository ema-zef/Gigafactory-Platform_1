import math


def calculate_machines(
    output_required,
    equipment,
    production
):

    # ----------------------------------
    # Production parameters
    # ----------------------------------

    hours_per_shift = float(
        production["hours_per_shift"]
    )

    shifts = int(
        production["no_of_shifts_per_day"]
    )

    available_minutes = float(
        production["available_time_min"]
    )

    if hours_per_shift <= 0:
        raise ValueError(
            "hours_per_shift must be greater than 0."
        )

    if shifts <= 0:
        raise ValueError(
            "no_of_shifts_per_day must be greater than 0."
        )

    if available_minutes <= 0:
        raise ValueError(
            "available_time_min must be greater than 0."
        )

    # ----------------------------------
    # Utilisation / uptime
    # ----------------------------------

    scheduled_minutes = (
        hours_per_shift
        * shifts
        * 60
    )

    uptime = (
        available_minutes
        / scheduled_minutes
    )

    # ----------------------------------
    # Equipment parameters
    # ----------------------------------

    category = (
        equipment["process_category"] or ""
    ).upper()

    speed = equipment["speed_m_min"]

    processing_time = equipment["processingtime_min"]
    
    capacity = equipment["Capacity"]

    # ----------------------------------
    # Capacity calculation
    # ----------------------------------

    if category == "ROLL":

        if speed is None or float(speed) <= 0:
            raise ValueError(
                f"{equipment['technology_name']} is ROLL equipment "
                f"but has invalid speed_m_min: {speed}"
            )

        speed = float(speed)

        daily_capacity = (
            speed
            * available_minutes
        )

        # Continuous process
        batches = None

    else:

        if (
            processing_time is None
            or float(processing_time) <= 0
        ):
            raise ValueError(
                f"{equipment['technology_name']} has invalid "
                f"processingtime_min: {processing_time}"
            )

        processing_time = float(
            processing_time
        )

        daily_capacity = ((
            available_minutes
            * capacity
            )
            / processing_time
        )

        # Only MASS processes are treated
        # as batch processes for now.
        if category == "MASS":
            batches = math.ceil(
                available_minutes
            / processing_time
            )
        else:
            batches = None

    # ----------------------------------
    # Safety check
    # ----------------------------------

    if daily_capacity <= 0:
        raise ValueError(
            f"Calculated daily capacity is {daily_capacity} "
            f"for {equipment['technology_name']}."
        )

    # ----------------------------------
    # Machine requirement
    # ----------------------------------

    machines = math.ceil(
        output_required
        / daily_capacity
    )

    # ----------------------------------
    # Return
    # ----------------------------------

    return {
        "machines": machines,
        "batches": batches,
        "shifts": shifts,
        "uptime": uptime,
        "daily_capacity_per_machine": daily_capacity
    }