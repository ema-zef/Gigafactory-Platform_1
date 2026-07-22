from fastapi import HTTPException


def calculate_capacity(product, production):

    annual_output_kwh = float(production["annual_output_kwh"])

    cell_capacity = float(product["cell_capacity_kwh"])

    annual_energy_kwh = annual_output_kwh * 1_000_000

    required_good_cells_year = annual_energy_kwh / cell_capacity

    required_good_cells_day = required_good_cells_year / 365

    return {

        "annual_output_kwh": annual_output_kwh,

        "required_good_cells_year": required_good_cells_year,

        "required_good_cells_day": required_good_cells_day

    }
    
def calculate_capacity(product, production):

    cell_capacity = float(product["cell_capacity_kwh"])

    annual_energy_kwh = (
        float(production["annual_output_kwh"])
        * 1_000_000
    )

    required_good_cells_year = (
        annual_energy_kwh / cell_capacity
    )

    required_good_cells_day = (
        required_good_cells_year / 365
    )

    return {

        "annual_energy_kwh": annual_energy_kwh,

        "required_good_cells_year":
            required_good_cells_year,

        "required_good_cells_day":
            required_good_cells_day

    }

# simulation/capacity.py

def calculate_required_material_flow(
    route,
    product,
    required_good_cells_day
):
    """
    Performs the backward material flow calculation.

    Parameters
    ----------
    route : list
        Manufacturing route (Cathode + Anode + Assembly)

    product : dict
        Product configuration row

    required_good_cells_day : float
        Target daily good cells

    Returns
    -------
    list
        Material flow for every technology
    """

    required_cells = required_good_cells_day

    simulation = []

    for equipment in reversed(route):

        quality = float(equipment["quality_rate"]) / 100

        if quality <= 0:
            quality = 1.0

        required_input_cells = required_cells / quality

        category = equipment["process_category"]

        # -----------------------------------------
        # CELL PROCESS
        # -----------------------------------------

        if category == "CELL":

            output = required_cells
            input_required = required_input_cells
            unit = "cells/day"

        # -----------------------------------------
        # CATHODE ROLL
        # -----------------------------------------

        elif category == "CATHODE_ROLL":

            output = (
                required_cells
                * product["number_of_electrodes_in_cell"]
                * product["cathode_length_mm"]
                / 1000
            )

            output /= quality

            input_required = output

            unit = "m/day"

        # -----------------------------------------
        # ANODE ROLL
        # -----------------------------------------

        elif category == "ANODE_ROLL":

            output = (
                required_cells
                * product["number_of_electrodes_in_cell"]
                * product["anode_length_mm"]
                / 1000
            )

            output /= quality

            input_required = output

            unit = "m/day"

        # -----------------------------------------
        # CATHODE MASS
        # -----------------------------------------

        elif category == "CATHODE_MASS":

            roll_length = (
                required_cells
                * product["number_of_electrodes_in_cell"]
                * product["cathode_length_mm"]
                / 1000
            )

            output = (
                roll_length
                * product["cath_coll_width_m"]
                * product["mass_load_cath_kg_m2"]
            )

            output /= quality

            input_required = output

            unit = "kg/day"

        # -----------------------------------------
        # ANODE MASS
        # -----------------------------------------

        elif category == "ANODE_MASS":

            roll_length = (
                required_cells
                * product["number_of_electrodes_in_cell"]
                * product["anode_length_mm"]
                / 1000
            )

            output = (
                roll_length
                * product["anode_coll_width_m"]
                * product["mass_load_anode_kg_m2"]
            )

            output /= quality

            input_required = output

            unit = "kg/day"

        # -----------------------------------------
        # DEFAULT
        # -----------------------------------------

        else:

            output = required_cells
            input_required = required_input_cells
            unit = "units/day"

        simulation.append({

            "equipment_id": equipment["equipment_id"],

            "technology_id": equipment["technology_id"],

            "technology_name": equipment["technology_name"],

            "process": equipment["process"],

            "category": category,

            "quality_rate": equipment["quality_rate"],

            "unit": unit,

            "required_output": round(output, 2),

            "required_input": round(input_required, 2)

        })

        required_cells = required_input_cells

    simulation.reverse()

    return simulation