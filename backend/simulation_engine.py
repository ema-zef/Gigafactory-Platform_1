# ==========================================
# simulation_engine.py
# ==========================================

# ------------------------------------------
# Cell calculations
# ------------------------------------------

def cells_per_year(
    annual_output_gwh,
    cell_capacity_kwh,
):

    annual_kwh = annual_output_gwh * 1_000_000

    return annual_kwh / cell_capacity_kwh


def cells_per_day(
    annual_output_gwh,
    cell_capacity_kwh,
):

    return (
        cells_per_year(
            annual_output_gwh,
            cell_capacity_kwh,
        )
        / 365
    )


# ------------------------------------------
# Quality compensation
# ------------------------------------------

def compensate_for_quality(
    output,
    quality_rate,
):

    if quality_rate is None:
        quality_rate = 100

    quality = float(quality_rate)

    if quality > 1:
        quality = quality / 100

    return output / quality


# ------------------------------------------
# Roll calculations
# ------------------------------------------

def cathode_roll_length(
    cells,
    cathode_length_mm,
    electrodes,
):

    return (
        cells
        * cathode_length_mm
        * electrodes
        / 1000
    )


def anode_roll_length(
    cells,
    anode_length_mm,
    electrodes,
):

    return (
        cells
        * anode_length_mm
        * electrodes
        / 1000
    )


def roll_to_cells(
    roll_length,
    electrode_length_mm,
    electrodes,
):

    return (
        roll_length
        * 1000
        / (
            electrode_length_mm
            * electrodes
        )
    )


# ------------------------------------------
# Mass calculations
# ------------------------------------------

def cathode_mass(
    roll_length,
    collector_width,
    mass_loading,
):

    return (
        roll_length
        * collector_width
        * mass_loading
    )


def anode_mass(
    roll_length,
    collector_width,
    mass_loading,
):

    return (
        roll_length
        * collector_width
        * mass_loading
    )


# ------------------------------------------
# Main process calculator
# ------------------------------------------

def calculate_process(
    category,
    required_cells,
    product,
    quality_rate,
):

    category = category.upper()

    # -------------------------
    # CELL
    # -------------------------

    if category == "CELL":

        output = required_cells

        input_required = compensate_for_quality(
            output,
            quality_rate,
        )

        next_cells = input_required

        unit = "Cells"

    # -------------------------
    # Cathode Roll
    # -------------------------

    elif category == "CATHODE_ROLL":

        output = cathode_roll_length(
            required_cells,
            product["cathode_length_mm"],
            product["number_of_electrodes_in_cell"],
        )

        input_required = compensate_for_quality(
            output,
            quality_rate,
        )

        next_cells = roll_to_cells(
            input_required,
            product["cathode_length_mm"],
            product["number_of_electrodes_in_cell"],
        )

        unit = "m"

    # -------------------------
    # Anode Roll
    # -------------------------

    elif category == "ANODE_ROLL":

        output = anode_roll_length(
            required_cells,
            product["anode_length_mm"],
            product["number_of_electrodes_in_cell"],
        )

        input_required = compensate_for_quality(
            output,
            quality_rate,
        )

        next_cells = roll_to_cells(
            input_required,
            product["anode_length_mm"],
            product["number_of_electrodes_in_cell"],
        )

        unit = "m"

    # -------------------------
    # Cathode Mass
    # -------------------------

    elif category == "CATHODE_MASS":

        roll = cathode_roll_length(
            required_cells,
            product["cathode_length_mm"],
            product["number_of_electrodes_in_cell"],
        )

        output = cathode_mass(
            roll,
            product["cath_coll_width_m"],
            product["mass_load_cath_kg_m2"],
        )

        input_required = compensate_for_quality(
            output,
            quality_rate,
        )

        next_cells = required_cells

        unit = "kg"

    # -------------------------
    # Anode Mass
    # -------------------------

    elif category == "ANODE_MASS":

        roll = anode_roll_length(
            required_cells,
            product["anode_length_mm"],
            product["number_of_electrodes_in_cell"],
        )

        output = anode_mass(
            roll,
            product["anode_coll_width_m"],
            product["mass_load_anode_kg_m2"],
        )

        input_required = compensate_for_quality(
            output,
            quality_rate,
        )

        next_cells = required_cells

        unit = "kg"

    # -------------------------
    # Default
    # -------------------------

    else:

        output = required_cells

        input_required = required_cells

        next_cells = required_cells

        unit = "Units"

    return {

        "output": output,

        "input": input_required,

        "next_cells": next_cells,

        "unit": unit,

    }