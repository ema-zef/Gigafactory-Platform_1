from fastapi import HTTPException


def calculate_capacity(product, production):
    cell_capacity = float(product["cell_capacity_kwh"])
    annual_energy_kwh = float(production["annual_output_kwh"]) * 1_000_000

    if cell_capacity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Cell capacity must be greater than zero.",
        )

    required_good_cells_year = annual_energy_kwh / cell_capacity
    required_good_cells_day = required_good_cells_year / 365

    return {
        "annual_energy_kwh": annual_energy_kwh,
        "required_good_cells_year": required_good_cells_year,
        "required_good_cells_day": required_good_cells_day,
    }


def calculate_required_material_flow(
    route,
    product,
    required_good_cells_day,
):
    """Perform the backward material-flow calculation."""

    required_cells = float(required_good_cells_day)
    simulation = []

    material_requirements = {
        "number_of_cells": required_good_cells_day,
        "cathode_active_material_kg": 0,
        "cathode_solvent_kg": 0,
        "cathode_additive_kg": 0,
        "cathode_binder_kg": 0,
        "cathode_collector_kg": 0,
        "anode_active_material_kg": 0,
        "anode_solvent_kg": 0,
        "anode_additive_kg": 0,
        "anode_binder_kg": 0,
        "anode_collector_kg": 0,
        "separator_kg": 0,
        "electrolyte_kg": 0,
        "housing_kg": 0,
        "housing_units": required_good_cells_day,
        "sealing_units": required_good_cells_day,
    }

    for equipment in reversed(route):
        quality = float(equipment.quality_rate) / 100

        if quality <= 0:
            quality = 1.0

        required_input_cells = required_cells / quality
        category = equipment.process_category
        process = (equipment.process or "").strip().upper()

        if category == "CELL":
            output = required_cells
            input_required = required_input_cells
            unit = "cells/day"

        elif category == "CATHODE_ROLL":
            roll_length = (
                required_cells
                * float(product["number_of_electrodes_in_cell"])
                * float(product["cathode_length_mm"])
                / 1000
            )

            required_roll_length = roll_length / quality
            output = required_roll_length
            input_required = required_roll_length
            unit = "m/day"

            # Current collector enters at coating.
            if process in ("COATING", "COATING & DRYING"):
                collector_width_m = float(product["cath_coll_width_m"])
                collector_kg_m2 = float(product["cathode_coll_kg_m2"])

                collector_area_m2 = (
                    required_roll_length * collector_width_m
                )

                material_requirements["cathode_collector_kg"] = round(
                    collector_area_m2 * collector_kg_m2,
                    4,
                )

        elif category == "ANODE_ROLL":
            roll_length = (
                required_cells
                * float(product["number_of_electrodes_in_cell"])
                * float(product["anode_length_mm"])
                / 1000
            )

            required_roll_length = roll_length / quality
            output = required_roll_length
            input_required = required_roll_length
            unit = "m/day"

            # Current collector enters at coating.
            if process in ("COATING", "COATING & DRYING"):
                collector_width_m = float(product["anode_coll_width_m"])
                collector_kg_m2 = float(product["anode_coll_kg_m2"])

                collector_area_m2 = (
                    required_roll_length * collector_width_m
                )

                material_requirements["anode_collector_kg"] = round(
                    collector_area_m2 * collector_kg_m2,
                    4,
                )

        elif category == "CATHODE_MASS":
            roll_length = (
                required_cells
                * float(product["number_of_electrodes_in_cell"])
                * float(product["cathode_length_mm"])
                / 1000
            )

            dry_cathode_mass = (
                roll_length
                * float(product["cath_coll_width_m"])
                * float(product["mass_load_cath_kg_m2"])
            ) / quality

            output = dry_cathode_mass
            input_required = dry_cathode_mass
            unit = "kg/day"

            active_fraction = float(product["cathode_am_w%"]) / 100
            additive_fraction = float(product["cathode_additive_w%"]) / 100
            binder_fraction = float(product["cathode_binder_w%"]) / 100
            solid_fraction = (
                float(product["cathode_solid_content_min_w%"]) / 100
            )

            if solid_fraction <= 0 or solid_fraction > 1:
                raise ValueError(
                    "Invalid cathode solid content: "
                    f"{product['cathode_solid_content_min_w%']}"
                )

            material_requirements["cathode_active_material_kg"] = round(
                dry_cathode_mass * active_fraction, 4
            )
            material_requirements["cathode_additive_kg"] = round(
                dry_cathode_mass * additive_fraction, 4
            )
            material_requirements["cathode_binder_kg"] = round(
                dry_cathode_mass * binder_fraction, 4
            )

            wet_cathode_mass = dry_cathode_mass / solid_fraction
            material_requirements["cathode_solvent_kg"] = round(
                wet_cathode_mass - dry_cathode_mass, 4
            )

        elif category == "ANODE_MASS":
            roll_length = (
                required_cells
                * float(product["number_of_electrodes_in_cell"])
                * float(product["anode_length_mm"])
                / 1000
            )

            dry_anode_mass = (
                roll_length
                * float(product["anode_coll_width_m"])
                * float(product["mass_load_anode_kg_m2"])
            ) / quality

            output = dry_anode_mass
            input_required = dry_anode_mass
            unit = "kg/day"

            active_fraction = float(product["anode_am_w%"]) / 100
            additive_fraction = float(product["anode_additive_w%"]) / 100
            binder_fraction = float(product["anode_binder_w%"]) / 100
            solid_fraction = (
                float(product["anode_solid_content_min_w%"]) / 100
            )

            if solid_fraction <= 0 or solid_fraction > 1:
                raise ValueError(
                    "Invalid anode solid content: "
                    f"{product['anode_solid_content_min_w%']}"
                )

            material_requirements["anode_active_material_kg"] = round(
                dry_anode_mass * active_fraction, 4
            )
            material_requirements["anode_additive_kg"] = round(
                dry_anode_mass * additive_fraction, 4
            )
            material_requirements["anode_binder_kg"] = round(
                dry_anode_mass * binder_fraction, 4
            )

            wet_anode_mass = dry_anode_mass / solid_fraction
            material_requirements["anode_solvent_kg"] = round(
                wet_anode_mass - dry_anode_mass, 4
            )

        else:
            output = required_cells
            input_required = required_input_cells
            unit = "units/day"

        simulation.append(
            {
                "technology_id": equipment.technology_id,
                "technology_name": equipment.technology_name,
                "process": equipment.process,
                "category": category,
                "quality_rate": equipment.quality_rate,
                "unit": unit,
                "required_output": round(output, 2),
                "required_input": round(input_required, 2),
            }
        )

        required_cells = required_input_cells

    simulation.reverse()

    # Cell-level material requirements.
    number_of_cells = float(required_good_cells_day)

    electrolyte_g_per_cell = float(
        product.get("electrolite_g_cell_min") or 0
    )
    separator_g_per_cell = float(
        product.get("separator_g_cell_min") or 0
    )
    housing_g_per_cell = float(
        product.get("housing_g_cell_min") or 0
    )

    material_requirements["electrolyte_kg"] = round(
        number_of_cells * electrolyte_g_per_cell / 1000,
        4,
    )
    material_requirements["separator_kg"] = round(
        number_of_cells * separator_g_per_cell / 1000,
        4,
    )
    material_requirements["housing_kg"] = round(
        number_of_cells * housing_g_per_cell / 1000,
        4,
    )

    return {
        "technologies": simulation,
        "material_requirements": material_requirements,
    }
