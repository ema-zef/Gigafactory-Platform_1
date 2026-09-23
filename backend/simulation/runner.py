from database import (
    load_product_configuration,
    load_production_configuration,
    load_equipment,
)

from simulation.capacity import (
    calculate_capacity,
    calculate_required_material_flow,
)

from simulation.machines import calculate_machines
from simulation.operators import calculate_operators
from simulation.energy import calculate_energy
from simulation.costs import calculate_costs
from simulation.carbon import calculate_carbon
from simulation.material_cost import calculate_material_costs
from simulation.bottleneck import identify_bottleneck


def run(request):

    # =========================================================
    # Load master data
    # =========================================================

    product = load_product_configuration(
        request.product_code
    )

    production = load_production_configuration(
        request.plant_code
    )
    
    print(
        "PRODUCTION COLUMNS:",
        production.keys()
    )

    print(
         "PRODUCTION CONFIG:",
         dict(production)
    )

    route = (
        request.cathode_route
        + request.anode_route
        + request.assembly_route
    )

    equipment_lookup = load_equipment(
        [
            step.technology_id
            for step in route
        ]
    )


    # =========================================================
    # Capacity
    # =========================================================

    capacity = calculate_capacity(
        product,
        production
    )

    required_good_cells_day = (
        capacity["required_good_cells_day"]
    )


    # =========================================================
    # Reverse material flow
    # =========================================================

    flow = calculate_required_material_flow(
        route=route,
        product=product,
        required_good_cells_day=required_good_cells_day
    )

    technologies = flow["technologies"]

    material_requirements = flow[
        "material_requirements"
    ]


    # =========================================================
    # Material costs
    # =========================================================
    #
    # Calculated ONCE per simulation, not once per technology.
    # =========================================================

    material_costs = calculate_material_costs(
        material_requirements,
        product
    )


    # =========================================================
    # Initialise totals
    # =========================================================

    total_machines = 0
    total_operators = 0

    total_electricity = 0
    total_gas = 0

    total_labour_cost = 0
    total_electricity_cost = 0
    total_gas_cost = 0
    total_overhead_cost = 0
    total_operating_cost = 0

    total_electricity_carbon = 0
    total_gas_carbon = 0
    total_carbon = 0


    # =========================================================
    # Technology calculations
    # =========================================================

    for tech in technologies:

        equipment = equipment_lookup[
            tech["technology_id"]
        ]


        # -----------------------------------------------------
        # Machines / batches / shifts
        # -----------------------------------------------------

        machines = calculate_machines(
            tech["required_output"],
            equipment,
            production,
        )


        # -----------------------------------------------------
        # Operators
        # -----------------------------------------------------

        operators = calculate_operators(
            machines["machines"],
            equipment,
        )


        # -----------------------------------------------------
        # Energy
        # -----------------------------------------------------

        energy = calculate_energy(
            machines,
            equipment,
            production,
        )


        # -----------------------------------------------------
        # Operating costs
        # -----------------------------------------------------

        costs = calculate_costs(
            machines,
            operators,
            energy,
            equipment,
            production,
        )


        # -----------------------------------------------------
        # Carbon
        # -----------------------------------------------------

        carbon = calculate_carbon(
            energy,
            production,
        )


        # -----------------------------------------------------
        # Add results to technology
        # -----------------------------------------------------

        tech["machines"] = machines

        tech["batches"] = machines.get(
            "batches"
        )

        tech["shifts"] = machines.get(
            "shifts"
        )

        tech["operators"] = operators

        tech["energy"] = energy

        tech["costs"] = costs

        tech["carbon"] = carbon


        # =====================================================
        # Aggregate machine/operator totals
        # =====================================================

        total_machines += (
            machines["machines"]
        )

        total_operators += (
            operators["operators_min"]
        )


        # =====================================================
        # Aggregate energy
        # =====================================================

        total_electricity += (
            energy["electricity"]
        )

        total_gas += (
            energy["gas"]
        )


        # =====================================================
        # Aggregate operating costs
        # =====================================================

        total_labour_cost += (
            costs["labour"]
        )

        total_electricity_cost += (
            costs["electricity"]
        )

        total_gas_cost += (
            costs["gas"]
        )

        total_overhead_cost += (
            costs["overhead"]
        )

        total_operating_cost += (
            costs["total"]
        )


        # =====================================================
        # Aggregate carbon
        # =====================================================

        total_electricity_carbon += (
            carbon["electricity"]
        )

        total_gas_carbon += (
            carbon["gas"]
        )

        total_carbon += (
            carbon["total"]
        )


    # =========================================================
    # Final totals
    # =========================================================

    total_energy = (
        total_electricity
        + total_gas
    )

    total_material_cost = (
        material_costs["total"]
    )

    total_cost = (
        total_operating_cost
        + total_material_cost
    )


    # =========================================================
    # Bottleneck
    # =========================================================

    bottleneck = identify_bottleneck(
        technologies
    )


    # =========================================================
    # Return
    # =========================================================

    return {

        # -----------------------------------------------------
        # Plant
        # -----------------------------------------------------

        "plant": {
            "plant_code": request.plant_code,

            "hours_per_shift":
                production["hours_per_shift"],

            "shifts_per_day":
                production["no_of_shifts_per_day"],

            "available_time_min":
                production["available_time_min"],
        },


        # -----------------------------------------------------
        # Product
        # -----------------------------------------------------

        "product": {
            "product_code":
                request.product_code,

            "cell_capacity_kwh":
                product["cell_capacity_kwh"],
        },


        # -----------------------------------------------------
        # Capacity
        # -----------------------------------------------------

        "capacity": capacity,


        # -----------------------------------------------------
        # Material requirements
        # -----------------------------------------------------

        "material_requirements":
            material_requirements,


        # -----------------------------------------------------
        # Technology results
        # -----------------------------------------------------

        "technologies":
            technologies,


        # -----------------------------------------------------
        # Overall results
        # -----------------------------------------------------

        "overall": {

            "machines":
                total_machines,

            "operators":
                total_operators,


            # -------------------------
            # Energy
            # -------------------------

            "energy": {

                "electricity": round(
                    total_electricity,
                    2
                ),

                "gas": round(
                    total_gas,
                    2
                ),

                "total": round(
                    total_energy,
                    2
                ),
            },


            # -------------------------
            # Costs
            # -------------------------

            "costs": {

                "operating": {

                    "labour": round(
                        total_labour_cost,
                        2
                    ),

                    "electricity": round(
                        total_electricity_cost,
                        2
                    ),

                    "gas": round(
                        total_gas_cost,
                        2
                    ),

                    "overhead": round(
                        total_overhead_cost,
                        2
                    ),

                    "total": round(
                        total_operating_cost,
                        2
                    ),
                },

                "materials":
                    material_costs,

                "total": round(
                    total_cost,
                    2
                ),
            },


            # -------------------------
            # Carbon
            # -------------------------

            "carbon": {

                "electricity": round(
                    total_electricity_carbon,
                    2
                ),

                "gas": round(
                    total_gas_carbon,
                    2
                ),

                "total": round(
                    total_carbon,
                    2
                ),
            },
        },


        # -----------------------------------------------------
        # Bottleneck
        # -----------------------------------------------------

        "bottleneck":
            bottleneck,
    }