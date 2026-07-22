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

    if equipment["category"] == "ROLL":
        speed = equipment["speed_m_min"]

        if speed is None or speed <= 0:
            raise ValueError(
                f"{equipment['technology_name']} has invalid speed_m_min: {speed}"
            )

        daily_capacity = speed * available_minutes

    else:
        processing_time = equipment["processingtime_min"]

        if processing_time is None or processing_time <= 0:
             raise ValueError(
                 f"{equipment['technology_name']} has invalid processingtime_min: {processing_time}"
             )

        daily_capacity = available_minutes / processing_time
    
    if daily_capacity <= 0:
        raise ValueError(
             f"Daily capacity is {daily_capacity} for {equipment['technology_name']}"
        )

machines = math.ceil(output_required / daily_capacity)
  

    machines = math.ceil(

        output_required /

        daily_capacity

    )

    return {

        "machines": machines,

        "uptime": uptime

    }