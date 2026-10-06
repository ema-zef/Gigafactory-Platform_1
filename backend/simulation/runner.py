from auth import User

from database import (
    load_product_configuration,
    load_product_material,
    load_production_configuration,
    load_equipment,
    load_environment_configurations,
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
from simulation.environment import calculate_environment


def run(request, user: User):

    # =========================================================
    # Load master data
    # =========================================================

    product = load_product_configuration(
        request.product_code,
        user.id,
    )

    product_material = load_product_material(
        request.product_code,
        user.id,
    )

    production = load_production_configuration(
        request.plant_code,
        user.id,
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

    # Environment is a route-step property. capacity.py carries it through
    # the reverse-flow calculation with the corresponding technology.
    requested_environment_types = {
        step.environment
        for step in route
        if step.environment != "none"
    }
    environment_configs = load_environment_configurations(
        requested_environment_types,
        user.id,
    )

    equipment_lookup = load_equipment(
        [step.technology_id for step in route],
        user.id,
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
        cathode_route=request.cathode_route,
        anode_route=request.anode_route,
        assembly_route=request.assembly_route,
        product=product,
        required_good_cells_day=required_good_cells_day
    )

    technologies = flow["technologies"]

    material_requirements = flow[
        "material_requirements"
    ]

    # Optional for compatibility with capacity.py versions without geometry.
    geometry = flow.get("geometry")


    # =========================================================
    # Material costs
    # =========================================================
    #
    # Calculated ONCE per simulation, not once per technology.
    # =========================================================

    material_costs = calculate_material_costs(
        material_requirements,
        product,
        product_material
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
    total_floor_space_cost = 0
    total_floor_space_m2 = 0
    total_operating_cost = 0

    total_electricity_carbon = 0
    total_gas_carbon = 0
    total_carbon = 0


    # =========================================================
    # Technology calculations
    # =========================================================

    environment_assignments = {key: [] for key in requested_environment_types}

    for tech_index, tech in enumerate(technologies):
        equipment = equipment_lookup[
            tech["technology_id"]
        ]

        environment_type = tech.get("environment", "none")

        # The equipment function converts lane-metres to parent-web metres only
        # for coating/calendaring; vacuum drying remains cycle based.
        side = tech.get("branch")
        machine_geometry = None
        if side in ("cathode", "anode"):
            side_geometry = (geometry or {}).get(side)
            if side_geometry is not None:
                machine_geometry = {
                    "collector_width_m": side_geometry["collector_width_m"],
                    "effective_parent_web_width_m": side_geometry["effective_parent_web_width_m"],
                    "electrode_web_input_length_m_day": tech["required_input"],
                }

        print(
            "MACHINE WIDTH DEBUG:",
            {
                "technology": tech["technology_name"],
                "branch": tech.get("branch"),
                "process": tech.get("process"),
                "equipment_web_width": equipment.get("web_width"),
                "product_parent_web_width":
                    product.get("effective_parent_web_width_m"),
                "machine_geometry": machine_geometry,
            },
        )

        machines = calculate_machines(
            tech["required_output"],
            equipment,
            production,
            geometry=machine_geometry,
        )
        

        operators = calculate_operators(
            machines["machines"],
            equipment,
        )

        energy = calculate_energy(
            machines,
            equipment,
            production,
        )

        costs = calculate_costs(
            machines,
            operators,
            energy,
            equipment,
            production,
        )

        carbon = calculate_carbon(
            energy,
            production,
        )

        tech["machines"] = machines
        tech["batches"] = machines.get("batches")
        tech["shifts"] = machines.get("shifts")
        tech["operators"] = operators
        tech["energy"] = energy
        tech["costs"] = costs
        tech["carbon"] = carbon

        if environment_type != "none":
            equipment_footprint_m2 = (
                float(machines["machines"] or 0)
                * float(equipment.get("equipment_floor_space_m_2") or 0)
            )
            environment_assignments[environment_type].append({
                "assignment_key": tech_index,
                "technology_id": tech["technology_id"],
                "technology_name": tech["technology_name"],
                "branch": tech.get("branch"),
                "equipment_footprint_m2": equipment_footprint_m2,
                "tech": tech,
            })
    
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

        total_floor_space_cost += (
            costs.get("floor_space", 0)
        )

        total_floor_space_m2 += (
            costs.get("floor_space_m2", 0)
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
    # Shared controlled-environment infrastructure
    # =========================================================

    environments = []
    for environment_type, assignments in environment_assignments.items():
        if not assignments:
            continue

        environment_result = calculate_environment(
            environment_type,
            environment_configs[environment_type],
            assignments,
            production,
        )
        environments.append(environment_result)

        env_energy = environment_result["energy"]
        env_costs = environment_result["costs"]
        env_carbon = environment_result["carbon"]

        # Count the shared infrastructure ONCE in factory totals.
        total_electricity += env_energy["electricity"]
        total_gas += env_energy["gas"]

        total_labour_cost += env_costs["labour"]
        total_electricity_cost += env_costs["electricity"]
        total_gas_cost += env_costs["gas"]
        total_overhead_cost += env_costs["overhead"]
        total_floor_space_cost += env_costs["floor_space"]
        total_floor_space_m2 += environment_result["controlled_area_m2"]
        total_operating_cost += env_costs["total"]

        total_electricity_carbon += env_carbon["electricity"]
        total_gas_carbon += env_carbon["gas"]
        total_carbon += env_carbon["total"]

        # Allocation is analytical attribution only. Do NOT add these values
        # to factory totals again.
        allocations = environment_result["allocations"]
        if len(allocations) != len(assignments):
            raise ValueError(
                f"Environment allocation mismatch for {environment_type}: "
                f"{len(assignments)} assignments, {len(allocations)} allocations"
            )

        for assignment, allocation in zip(assignments, allocations):
            assignment["tech"]["environment_allocation"] = allocation

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

        # Electrode geometry and coating/collector breakdown.
        "geometry": geometry,


        # -----------------------------------------------------
        # Technology results
        # -----------------------------------------------------

        "technologies":
            technologies,

        # Shared controlled-environment infrastructure.
        "environments": environments,


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

                    "floor_space": round(
                        total_floor_space_cost,
                        2
                    ),

                    "floor_space_m2": round(
                        total_floor_space_m2,
                        4
                    ),

                    "environment": round(
                        sum(env["costs"]["total"] for env in environments),
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