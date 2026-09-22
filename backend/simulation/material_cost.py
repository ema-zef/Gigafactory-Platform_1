def calculate_material_costs(
    material_requirements,
    product
):

    # =========================================================
    # Helper
    # =========================================================

    def get_float(data, key, default=0):
        value = data.get(key, default)

        if value is None:
            return float(default)

        return float(value)


    # =========================================================
    # Required material quantities
    # =========================================================

    # Cathode
    cathode_active_kg = get_float(
        material_requirements,
        "cathode_active_material_kg"
    )

    cathode_solvent_kg = get_float(
        material_requirements,
        "cathode_solvent_kg"
    )

    cathode_additive_kg = get_float(
        material_requirements,
        "cathode_additive_kg"
    )

    cathode_binder_kg = get_float(
        material_requirements,
        "cathode_binder_kg"
    )

    cathode_collector_kg = get_float(
        material_requirements,
        "cathode_collector_kg"
    )


    # Anode
    anode_active_kg = get_float(
        material_requirements,
        "anode_active_material_kg"
    )

    anode_solvent_kg = get_float(
        material_requirements,
        "anode_solvent_kg"
    )

    anode_additive_kg = get_float(
        material_requirements,
        "anode_additive_kg"
    )

    anode_binder_kg = get_float(
        material_requirements,
        "anode_binder_kg"
    )

    anode_collector_kg = get_float(
        material_requirements,
        "anode_collector_kg"
    )


    # Assembly
    separator_kg = get_float(
        material_requirements,
        "separator_kg"
    )

    number_of_cells = get_float(
        material_requirements,
        "number_of_cells"
    )


    # =========================================================
    # Material prices
    # =========================================================

    # Cathode
    cathode_price = get_float(
        product,
        "cath_prec_material_price_€"
    )

    cathode_solvent_price = get_float(
        product,
        "solvent_price_c"
    )

    cathode_additive_price = get_float(
        product,
        "additive_price"
    )

    cathode_binder_price = get_float(
        product,
        "binder_price"
    )

    cathode_collector_price = get_float(
        product,
        "cathode_collector_price_e_kg"
    )


    # Anode
    anode_price = get_float(
        product,
        "ano_raw_material_price_€"
    )

    anode_solvent_price = get_float(
        product,
        "solvent_price_a"
    )

    anode_additive_price = get_float(
        product,
        "additive_price"
    )

    anode_binder_price = get_float(
        product,
        "binder_price"
    )

    anode_collector_price = get_float(
        product,
        "anode_collector_price_e_kg"
    )


    # Assembly
    separator_kg = get_float(
        material_requirements,
        "separator_kg"
        )

    housing_kg = get_float(
        material_requirements,
        "housing_kg"
        )

    electrolyte_kg = get_float(
        material_requirements,
        "electrolyte_kg"
    )

    sealing_price = get_float(
        product,
        "sealing_price"
    )


    # =========================================================
    # Cathode material costs
    # =========================================================

    cathode_active_cost = (
        cathode_active_kg
        * cathode_price
    )

    cathode_solvent_cost = (
        cathode_solvent_kg
        * cathode_solvent_price
    )

    cathode_additive_cost = (
        cathode_additive_kg
        * cathode_additive_price
    )

    cathode_binder_cost = (
        cathode_binder_kg
        * cathode_binder_price
    )

    cathode_collector_cost = (
        cathode_collector_kg
        * cathode_collector_price
    )

    cathode_total = (
        cathode_active_cost
        + cathode_solvent_cost
        + cathode_additive_cost
        + cathode_binder_cost
        + cathode_collector_cost
    )

    
    cathode_composition = (
       active_fraction
       + additive_fraction
       + binder_fraction
    )

if abs(cathode_composition - 1.0) > 0.01:
    raise ValueError(
        f"Cathode composition does not sum to 100%. "
        f"Current total: "
        f"{cathode_composition * 100:.2f}%"
    )
    
    # =========================================================
    # Anode material costs
    # =========================================================

    anode_active_cost = (
        anode_active_kg
        * anode_price
    )

    anode_solvent_cost = (
        anode_solvent_kg
        * anode_solvent_price
    )

    anode_additive_cost = (
        anode_additive_kg
        * anode_additive_price
    )

    anode_binder_cost = (
        anode_binder_kg
        * anode_binder_price
    )

    anode_collector_cost = (
        anode_collector_kg
        * anode_collector_price
    )

    anode_total = (
        anode_active_cost
        + anode_solvent_cost
        + anode_additive_cost
        + anode_binder_cost
        + anode_collector_cost
    )

    anode_composition = (
        active_fraction
        + additive_fraction
        + binder_fraction
    )

if abs(anode_composition - 1.0) > 0.01:
    raise ValueError(
        f"Anode composition does not sum to 100%. "
        f"Current total: "
        f"{anode_composition * 100:.2f}%"
    )


    # =========================================================
    # Assembly material costs
    # =========================================================

    separator_cost = (
        separator_kg
        * separator_price
    )

    housing_cost = (
        housing_kg
        * housing_price
    )

    electrolyte_cost = (
        electrolyte_kg
        * electrolyte_price
    )

    sealing_cost = (
        number_of_cells
        * sealing_price
    )

    assembly_total = (
        separator_cost
        + housing_cost
        + electrolyte_cost
        + sealing_cost
    )


    # =========================================================
    # Total material cost
    # =========================================================

    total = (
        cathode_total
        + anode_total
        + assembly_total
    )


    # =========================================================
    # Return
    # =========================================================

    return {

        "cathode": {
            "active_material": round(
                cathode_active_cost, 2
            ),
            "solvent": round(
                cathode_solvent_cost, 2
            ),
            "additive": round(
                cathode_additive_cost, 2
            ),
            "binder": round(
                cathode_binder_cost, 2
            ),
            "collector": round(
                cathode_collector_cost, 2
            ),
            "total": round(
                cathode_total, 2
            )
        },

        "anode": {
            "active_material": round(
                anode_active_cost, 2
            ),
            "solvent": round(
                anode_solvent_cost, 2
            ),
            "additive": round(
                anode_additive_cost, 2
            ),
            "binder": round(
                anode_binder_cost, 2
            ),
            "collector": round(
                anode_collector_cost, 2
            ),
            "total": round(
                anode_total, 2
            )
        },

        "assembly": {
            "separator": round(
                separator_cost, 2
            ),
            "housing": round(
                housing_cost, 2
            ),
            "electrolyte": round(
                electrolyte_cost, 2
            ),
            "sealing": round(
                sealing_cost, 2
            ),
            "total": round(
                assembly_total, 2
            )
        },

        "total": round(
            total, 2
        )
    }