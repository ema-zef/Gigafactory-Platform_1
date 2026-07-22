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

    if equipment["speed_m_min"] is not None:
        daily_capacity = (
            equipment["speed_m_min"]
            * available_minutes
       )
    else:
        daily_capacity = (
            available_minutes
            / equipment["processingtime_min"]
        )

    machines = math.ceil(

        output_required /

        daily_capacity

    )

    return {

        "machines": machines,

        "uptime": uptime

    }