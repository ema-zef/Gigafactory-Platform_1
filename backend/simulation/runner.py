from database import (

    load_product_configuration,

    load_production_configuration,

    load_equipment

)

from simulation.capacity import calculate_capacity

from simulation.machines import calculate_machines

from simulation.operators import calculate_operators

from simulation.energy import calculate_energy

from simulation.costs import calculate_costs

from simulation.carbon import calculate_carbon

from simulation.bottleneck import identify_bottleneck


def run(request):

    product = load_product_configuration(

        request.product_code

    )

    production = load_production_configuration(

        request.plant_code

    )

    equipment_lookup = load_equipment(

        [

            step["technology_id"]

            for step in

            request.cathode_route

            +

            request.anode_route

            +

            request.assembly_route

        ]

    )

    capacity = calculate_capacity(

        product,

        production

    )

    technologies = []

    for step in (

        request.cathode_route

        +

        request.anode_route

        +

        request.assembly_route

    ):

        equipment = equipment_lookup[

            step["technology_id"]

        ]

        machines = calculate_machines(

            capacity["required_good_cells_day"],

            equipment,

            production

        )

        operators = calculate_operators(

            machines["machines"],

            equipment

        )

        energy = calculate_energy(

            machines,

            equipment,

            production

        )

        costs = calculate_costs(

            machines,

            operators,

            energy,

            production

        )

        carbon = calculate_carbon(

            energy,

            production

        )

        technologies.append({

            "technology":

                step["technology_name"],

            "machines":

                machines,

            "operators":

                operators,

            "energy":

                energy,

            "costs":

                costs,

            "carbon":

                carbon

        })

    bottleneck = identify_bottleneck(

        technologies

    )

    return {

        "plant": production,

        "product": product,

        "capacity": capacity,

        "technologies": technologies,

        "bottleneck": bottleneck

    }
    
from simulation.capacity import (
    calculate_capacity,
    calculate_required_material_flow
)

capacity = calculate_capacity(
    product,
    production
)

simulation = calculate_required_material_flow(
    route=route,
    product=product,
    required_good_cells_day=capacity["required_good_cells_day"]
)

return {

    "plant": plant_summary,

    "product": product_summary,

    "technologies": technologies,

    "overall": overall_summary,

    "bottleneck": bottleneck,

    "costs": costs,

    "energy": energy,

    "carbon": carbon

}

plant_summary = {

    "code": plant_code,

    "hours_per_shift": hours_per_shift,

    "shifts_per_day": shifts_per_day,

    "available_time_min": available_time_min,

    "uptime": round(uptime * 100,2),

    "operator_rate": production["operator_rate"],

    "electricity_cost": {

        "min": production["electricity_cost_rate_min_eur_per_kwh"],

        "max": production["electricity_cost_rate_max_eur_per_kwh"]

    },

    "gas_cost": {

        "min": production["gas_cost_rate_min_eur_per_kwh"],

        "max": production["gas_cost_rate_max_eur_per_kwh"]

    },

    "floor_space_cost": production["floor_space_cost_rate_eur_per_m2"],

    "ghge": {

        "electricity": production["elec_ghge_rate"],

        "gas": production["gas_ghge_rate"]

    }

}

product_summary = {

    "code": product_code,

    "cell_capacity_kwh": product["cell_capacity_kwh"],

    "good_cells_day": round(required_good_cells_day,2)

}

overall_summary = {

    "daily_output": round(

        technologies[-1]["required_output"],

        2

    ),

    "machines": overall_machines,

    "operators": overall_operators,

    "uptime": round(uptime*100,2)

}

