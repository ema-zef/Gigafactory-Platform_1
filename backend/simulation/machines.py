import math


def calculate_machines(

    output_required,

    equipment,

    production

):

    hours_per_shift = float(

        production["hours_per_shift"]

    )

    shifts = int(

        production["no_of_shifts_per_day"]

    )

    available_minutes = float(

        production["available_time_min"]

    )

    uptime = available_minutes / (

        hours_per_shift *

        shifts *

        60

    )

    speed = equipment["speed_m_min"]
    processing_time = equipment["processingtime_min"]

    if speed is not None and speed > 0:
        daily_capacity = speed * available_minutes

    elif processing_time is not None and processing_time > 0:
         daily_capacity = available_minutes / processing_time

    else:
        raise ValueError(
            f"{equipment['technology_name']} has neither a valid speed_m_min "
            f"nor processingtime_min."
        )

    machines = math.ceil(output_required / daily_capacity)

    return {
        "machines": machines,

        "uptime": uptime

    }