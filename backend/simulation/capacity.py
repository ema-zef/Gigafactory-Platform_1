"""Daily capacity and independent cathode/anode/assembly material flows."""
from fastapi import HTTPException


def _number(row, key, *, positive=False, default=None):
    value = row.get(key) if hasattr(row, "get") else row[key]
    if value is None:
        if default is not None:
            return default
        raise ValueError(f"Missing product/production field: {key}")
    number = float(value)
    if positive and number <= 0:
        raise ValueError(f"{key} must be greater than zero; received {value}")
    return number


def calculate_capacity(product, production):
    cell_capacity = _number(product, "cell_capacity_kwh", positive=True)
    annual_energy_kwh = _number(production, "annual_output_kwh", positive=True) * 1_000_000
    good_cells_year = annual_energy_kwh / cell_capacity
    return {
        "annual_energy_kwh": annual_energy_kwh,
        "required_good_cells_year": good_cells_year,
        "required_good_cells_day": good_cells_year / 365,
    }


def _step_value(step, name, default=None):
    if isinstance(step, dict):
        return step.get(name, default)
    return getattr(step, name, default)


def _reverse_route(steps, finished_output, unit, branch):
    """Reverse one independent branch; quantities share the specified unit."""
    required_output = finished_output
    results = []
    for step in reversed(steps):
        quality_percent = float(_step_value(step, "quality_rate", 100) or 0)
        if not 0 < quality_percent <= 100:
            raise ValueError(
                f"Invalid quality_rate={quality_percent} for "
                f"{_step_value(step, 'technology_name', 'unknown technology')}"
            )
        required_input = required_output / (quality_percent / 100)
        results.append({
            "technology_id": _step_value(step, "technology_id"),
            "technology_name": _step_value(step, "technology_name"),
            "process": _step_value(step, "process"),
            "category": _step_value(step, "process_category"),
            "branch": branch,
            "quality_rate": quality_percent,
            "unit": unit,
            "required_output": round(required_output, 6),
            "required_input": round(required_input, 6),
        })
        required_output = required_input
    results.reverse()
    return results, required_output


def _electrode_geometry(product, side):
    electrode_count = _number(product, "number_of_electrodes_in_cell", positive=True)
    length_m = _number(product, f"{side}_length_mm", positive=True) / 1000
    width_key = "cath_coll_width_m" if side == "cathode" else "anode_coll_width_m"
    width_m = _number(product, width_key, positive=True)
    loading_key = "mass_load_cath_kg_m2" if side == "cathode" else "mass_load_anode_kg_m2"
    loading = _number(product, loading_key, positive=True)
    return electrode_count * length_m, width_m, loading


def _electrode_materials(product, side, wet_slurry_kg, collector_length_m, width_m, materials):
    prefix = side
    active = _number(product, f"{prefix}_am_w%") / 100
    additive = _number(product, f"{prefix}_additive_w%") / 100
    binder = _number(product, f"{prefix}_binder_w%") / 100
    solids = _number(product, f"{prefix}_solid_content_min_w%", positive=True) / 100
    if not 0 < solids <= 1:
        raise ValueError(f"Invalid {prefix} solid content: {solids * 100}%")
    if any(x < 0 or x > 1 for x in (active, additive, binder)):
        raise ValueError(f"Invalid {prefix} dry composition fractions")
    if abs(active + additive + binder - 1) > 0.02:
        raise ValueError(f"{prefix} dry composition must sum to approximately 100%")
    dry_kg = wet_slurry_kg * solids
    materials[f"{prefix}_active_material_kg"] = round(dry_kg * active, 4)
    materials[f"{prefix}_additive_kg"] = round(dry_kg * additive, 4)
    materials[f"{prefix}_binder_kg"] = round(dry_kg * binder, 4)
    materials[f"{prefix}_solvent_kg"] = round(wet_slurry_kg - dry_kg, 4)
    collector_key = "cathode_coll_kg_m2" if side == "cathode" else "anode_coll_kg_m2"
    collector_kg_m2 = _number(product, collector_key, positive=True)
    materials[f"{prefix}_collector_kg"] = round(collector_length_m * width_m * collector_kg_m2, 4)


def calculate_required_material_flow(
    route=None,
    product=None,
    required_good_cells_day=None,
    *,
    cathode_route=None,
    anode_route=None,
    assembly_route=None,
):
    """Calculate independent branches and return the existing dashboard schema.

    Each electrode branch ends at the assembly input. Product loading is
    assumed to be dry coating kg/m² and mixing capacity wet slurry kg/cycle.
    Confirm these source-data units before treating machine counts as validated.
    """
    if route is not None and any(x is None for x in (cathode_route, anode_route, assembly_route)):
        raise ValueError("Pass cathode_route, anode_route and assembly_route separately, not one serial route")
    if product is None or required_good_cells_day is None:
        raise ValueError("product and required_good_cells_day are required")
    cathode_route = cathode_route or []
    anode_route = anode_route or []
    assembly_route = assembly_route or []
    if not cathode_route or not anode_route or not assembly_route:
        raise ValueError("Cathode, anode and assembly routes must each contain equipment")

    good_cells = float(required_good_cells_day)
    if good_cells <= 0:
        raise ValueError("required_good_cells_day must be positive")
    materials = {
        "number_of_cells": good_cells,
        "cathode_active_material_kg": 0, "cathode_solvent_kg": 0,
        "cathode_additive_kg": 0, "cathode_binder_kg": 0,
        "cathode_collector_kg": 0, "anode_active_material_kg": 0,
        "anode_solvent_kg": 0, "anode_additive_kg": 0,
        "anode_binder_kg": 0, "anode_collector_kg": 0,
        "separator_kg": 0, "electrolyte_kg": 0, "housing_kg": 0,
        "housing_units": good_cells, "sealing_units": good_cells,
    }

    assembly_results, assembly_input_cells = _reverse_route(
        assembly_route, good_cells, "cells/day", "assembly"
    )
    branch_results = []
    for side, steps in (("cathode", cathode_route), ("anode", anode_route)):
        metres_per_cell, width_m, loading_kg_m2 = _electrode_geometry(product, side)
        assembly_input_length = assembly_input_cells * metres_per_cell
        roll_steps = [s for s in steps if (_step_value(s, "process_category") or "").upper() == "ROLL"]
        mass_steps = [s for s in steps if (_step_value(s, "process_category") or "").upper() == "MASS"]
        if not roll_steps or not mass_steps:
            raise ValueError(f"{side} route needs MASS mixing and ROLL equipment")

        roll_results, roll_input_length = _reverse_route(
            roll_steps, assembly_input_length, "m/day", side
        )
        # Coating introduces the collector. Its input web length is the
        # purchased collector requirement; earlier roll steps are not counted twice.
        coating = next(
            (s for s in roll_results if "COAT" in (s["process"] or "").upper()), None
        )
        if coating is None:
            raise ValueError(f"{side} route has no coating step")
        collector_length = coating["required_input"]

        # Wet slurry must cover the coating input web, including coating yield.
        dry_coating_kg = collector_length * width_m * loading_kg_m2
        solids_key = f"{side}_solid_content_min_w%"
        solids = _number(product, solids_key, positive=True) / 100
        if not 0 < solids <= 1:
            raise ValueError(f"Invalid {solids_key}: {solids * 100}%")
        slurry_for_coating_kg = dry_coating_kg / solids
        mass_results, wet_slurry_input = _reverse_route(
            mass_steps, slurry_for_coating_kg, "kg/day", side
        )
        _electrode_materials(
            product, side, wet_slurry_input, collector_length, width_m, materials
        )
        # Keep the original user-defined order within each branch.
        by_id = {s["technology_id"]: s for s in mass_results + roll_results}
        branch_results.extend(by_id[_step_value(s, "technology_id")] for s in steps)

    # Cell-level materials currently use finished-cell demand, consistent with
    # the previous implementation. Move to each introduction step if waste
    # accounting for separator/electrolyte/housing is required.
    for result_key, product_key in (
        ("electrolyte_kg", "electrolite_g_cell_min"),
        ("separator_kg", "separator_g_cell_min"),
        ("housing_kg", "housing_g_cell_min"),
    ):
        materials[result_key] = round(
            good_cells * _number(product, product_key, default=0) / 1000, 4
        )
    return {
        "technologies": branch_results + assembly_results,
        "material_requirements": materials,
    }
