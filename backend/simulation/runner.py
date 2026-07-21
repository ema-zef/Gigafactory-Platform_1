from database import (
    load_product_configuration,
    load_production_configuration,
    load_equipment
)

from simulation.capacity import (
    calculate_capacity,
    calculate_required_material_flow
)

from simulation.machines import calculate_machines
from simulation.operators import calculate_operators
from simulation.energy import calculate_energy
from simulation.costs import calculate_costs
from simulation.carbon import calculate_carbon
from simulation.bottleneck import identify_bottleneck


def run(request):

    # ----------------------------------
    # Load master data
    # ----------------------------------

    product = load_product_configuration(
        request.product_code
    )

    production = load_production_configuration(
        request.plant_code
    )

    route = (
        request.cathode_route +
        request.anode_route +
        request.assembly_route
    )

    equipment_lookup = load_equipment(
        [
            step.technology_id
            for step in route
        ]
    )

    # ----------------------------------
    # Capacity
    # ----------------------------------

    capacity = calculate_capacity(
        product,
        production
    )

    required_good_cells_day = capacity["required_good_cells_day"]

    # ----------------------------------
    # Material Flow
    # ----------------------------------

    technologies = calculate_required_material_flow(
        route=route,
        product=product,
        required_good_cells_day=required_good_cells_day
    )

    # ----------------------------------
    # Machine / Operator / Energy / Cost
    # ----------------------------------

    total_machines = 0
    total_operators = 0
    total_energy = 0
    total_cost = 0
    total_carbon = 0

    for tech in technologies:

        equipment = equipment_lookup[
            tech["technology_id"]
        ]

        machines = calculate_machines(
            tech["required_output"],
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

        tech["machines"] = machines
        tech["operators"] = operators
        tech["energy"] = energy
        tech["costs"] = costs
        tech["carbon"] = carbon

        total_machines += machines["machines"]
        total_operators += operators["operators"]
        total_energy += energy["daily_energy_kwh"]
        total_cost += costs["daily_cost_eur"]
        total_carbon += carbon["daily_carbon_kg"]

    # ----------------------------------
    # Bottleneck
    # ----------------------------------

    bottleneck = identify_bottleneck(
        technologies
    )

    # ----------------------------------
    # Plant Summary
    # ----------------------------------

    available_time = (
        production["hours_per_shift"] *
        production["shifts_per_day"] *
        60
    )

    plant_summary = {

        "plant_code": request.plant_code,

        "hours_per_shift":
            production["hours_per_shift"],

        "shifts_per_day":
            production["shifts_per_day"],

        "uptime":
            production["uptime"],

        "available_time_min":
            available_time,

        "operator_rate":
            production["operator_rate"],

        "electricity_cost": {
            "min":
                production["electricity_cost_rate_min_eur_per_kwh"],
            "max":
                production["electricity_cost_rate_max_eur_per_kwh"]
        },

        "gas_cost": {
            "min":
                production["gas_cost_rate_min_eur_per_kwh"],
            "max":
                production["gas_cost_rate_max_eur_per_kwh"]
        },

        "floor_space_cost":
            production["floor_space_cost_rate_eur_per_m2"],

        "ghge": {
            "electricity":
                production["elec_ghge_rate"],
            "gas":
                production["gas_ghge_rate"]
        }

    }

    # ----------------------------------
    # Product Summary
    # ----------------------------------

    product_summary = {

        "product_code":
            request.product_code,

        "cell_capacity_kwh":
            product["cell_capacity_kwh"],

        "required_good_cells_day":
            required_good_cells_day

    }

    # ----------------------------------
    # Overall Summary
    # ----------------------------------

    overall_summary = {

        "machines":
            total_machines,

        "operators":
            total_operators,

        "energy_kwh":
            total_energy,

        "cost_eur":
            total_cost,

        "carbon_kg":
            total_carbon

    }

    # ----------------------------------
    # Return
    # ----------------------------------

    return {

        "plant":
            plant_summary,

        "product":
            product_summary,

        "capacity":
            capacity,

        "technologies":
            technologies,

        "overall":
            overall_summary,

        "bottleneck":
            bottleneck

    }