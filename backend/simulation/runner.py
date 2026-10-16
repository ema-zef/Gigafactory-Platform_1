from auth import User
from math import ceil

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

    # Validate the operating calendar loaded from Production_Configuration.
    from math import isfinite
    from fastapi import HTTPException
    try:
        raw_days = production["number_of_days_per_year"]
        days_float = float(raw_days)
        if not isfinite(days_float) or not days_float.is_integer():
            raise ValueError("must be a whole number")
        number_of_days_per_year = int(days_float)
        if not 1 <= number_of_days_per_year <= 366:
            raise ValueError("must be between 1 and 366")
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid production_configuration.number_of_days_per_year: {exc}",
        ) from exc

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
        if step.execution_mode == "in_house" and step.environment != "none"
    }
    environment_configs = load_environment_configurations(
        requested_environment_types,
        user.id,
    )

    equipment_lookup = load_equipment(
        [step.technology_id for step in route if step.execution_mode == "in_house" and step.technology_id is not None],
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
        if tech.get("execution_mode", "in_house") != "in_house":
            continue
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

    external_processing = flow.get("external_processing", [])

    # Purchased electrode rolls are purchased materials, not external processing
    # services. Keep their freight in external processing, and never double count.
    purchased_electrodes = {"cathode": 0.0, "anode": 0.0}
    external_cost = 0.0
    for item in external_processing:
        if (item.get("mode") == "purchased_intermediate"
                and item.get("branch") in purchased_electrodes):
            branch = item["branch"]
            purchase_cost = float(item.get("processing_or_purchase_cost") or 0)
            purchased_electrodes[branch] += purchase_cost
            # Preserve any other components of total_cost (normally transport).
            external_cost += float(item["total_cost"]) - purchase_cost
        else:
            external_cost += float(item["total_cost"])

    purchased_electrode_total = sum(purchased_electrodes.values())
    # Copy the material-cost structure so the existing calculation stays intact.
    material_costs = dict(material_costs)
    for branch, purchase_cost in purchased_electrodes.items():
        branch_costs = dict(material_costs.get(branch) or {})
        branch_costs["purchased_electrode_roll"] = round(purchase_cost, 2)
        branch_costs["total"] = round(
            float(branch_costs.get("total") or 0) + purchase_cost, 2
        )
        material_costs[branch] = branch_costs
    material_costs["purchased_electrodes"] = {
        "cathode": round(purchased_electrodes["cathode"], 2),
        "anode": round(purchased_electrodes["anode"], 2),
        "total": round(purchased_electrode_total, 2),
    }
    material_costs["total"] = round(
        float(material_costs["total"]) + purchased_electrode_total, 2
    )
    total_material_cost = float(material_costs["total"])
    external_carbon = sum(item["carbon_kgco2e"] for item in external_processing)
    # Plant-level headcount: preserve process FTE demand, but employ whole people.
    # Individual technology costs remain analytical FTE allocations. The additional
    # half/full FTE payroll and overhead are added only once at plant level.
    operator_demand_fte = float(total_operators)
    required_operators = ceil(operator_demand_fte - 1e-9)
    unused_operator_fte = max(0.0, required_operators - operator_demand_fte)
    operator_utilization_pct = (
        100.0 * operator_demand_fte / required_operators
        if required_operators else 0.0
    )

    # Derive the existing daily per-FTE labour cost from the technology totals.
    # This keeps the adjustment consistent with simulation.costs without
    # assuming whether operator_rate is per hour, shift, or another unit.
    technology_labour_cost = sum(
        float(t["costs"]["labour"])
        for t in technologies
        if t.get("execution_mode", "in_house") == "in_house"
    )
    daily_labour_cost_per_fte = (
        technology_labour_cost / operator_demand_fte
        if operator_demand_fte > 0 else 0.0
    )
    extra_labour_cost = unused_operator_fte * daily_labour_cost_per_fte

    # Match the configured overhead treatment for incremental payroll.
    overhead_percentage = float(production["Cost_Overhead_Factor_(%)"])
    extra_overhead_cost = extra_labour_cost * overhead_percentage / 100.0

    total_labour_cost += extra_labour_cost
    total_overhead_cost += extra_overhead_cost
    total_operating_cost += extra_labour_cost + extra_overhead_cost
    total_cost = total_operating_cost + total_material_cost + external_cost


    # =========================================================
    # Bottleneck
    # =========================================================

    bottleneck = identify_bottleneck(
        [t for t in technologies if t.get("execution_mode", "in_house") == "in_house"]
    ) if any(t.get("execution_mode", "in_house") == "in_house" for t in technologies) else None


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

            "number_of_days_per_year": number_of_days_per_year,
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
        "external_processing": external_processing,
        "production_mode": flow.get("production_mode", "finished_cells"),

        # Shared controlled-environment infrastructure.
        "environments": environments,


        # -----------------------------------------------------
        # Overall results
        # -----------------------------------------------------

        "overall": {

            "machines":
                total_machines,

            "operators":
                required_operators,

            "operator_utilization": {
                "required_fte": round(operator_demand_fte, 4),
                "headcount": required_operators,
                "utilization_percent": round(operator_utilization_pct, 2),
                "unused_fte": round(unused_operator_fte, 4),
                # Accounting illustration, not a person-specific shift assignment.
                "underutilized_operator": (
                    {
                        "operator_number": required_operators,
                        "utilization_percent": round(
                            100.0 * (1.0 - unused_operator_fte), 2
                        ),
                    }
                    if unused_operator_fte > 1e-9 else None
                ),
                "additional_labour_cost_per_day": round(extra_labour_cost, 2),
                "additional_overhead_cost_per_day": round(extra_overhead_cost, 2),
            },


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
                "external_processing": round(external_cost, 2),

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

                "external_processing": round(external_carbon, 2),
                "total": round(
                    total_carbon + external_carbon,
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