def calculate_material_costs(material_requirements, product):
    """Calculate daily material costs from process-derived material quantities."""

    def get_float(data, key, default=0.0):
        value = data.get(key, default)
        if value is None or value == "":
            return float(default)
        return float(value)

    # Required quantities (kg/day unless noted)
    cathode_active_kg = get_float(material_requirements, "cathode_active_material_kg")
    cathode_solvent_kg = get_float(material_requirements, "cathode_solvent_kg")
    cathode_additive_kg = get_float(material_requirements, "cathode_additive_kg")
    cathode_binder_kg = get_float(material_requirements, "cathode_binder_kg")
    cathode_collector_kg = get_float(material_requirements, "cathode_collector_kg")

    anode_active_kg = get_float(material_requirements, "anode_active_material_kg")
    anode_solvent_kg = get_float(material_requirements, "anode_solvent_kg")
    anode_additive_kg = get_float(material_requirements, "anode_additive_kg")
    anode_binder_kg = get_float(material_requirements, "anode_binder_kg")
    anode_collector_kg = get_float(material_requirements, "anode_collector_kg")

    separator_kg = get_float(material_requirements, "separator_kg")
    housing_kg = get_float(material_requirements, "housing_kg")
    electrolyte_kg = get_float(material_requirements, "electrolyte_kg")
    number_of_cells = get_float(material_requirements, "number_of_cells")

    # Collector quantities above are GROSS purchased foil (usable + trim).
    cathode_trim_kg = get_float(material_requirements, "cathode_collector_trim_kg")
    anode_trim_kg = get_float(material_requirements, "anode_collector_trim_kg")
    if cathode_trim_kg > cathode_collector_kg or anode_trim_kg > anode_collector_kg:
        raise ValueError("Collector trim cannot exceed gross purchased collector mass")

    # Prices
    cathode_price = get_float(product, "cath_prec_material_price_€")
    cathode_solvent_price = get_float(product, "solvent_price_c")
    cathode_additive_price = get_float(product, "additive_price")
    cathode_binder_price = get_float(product, "binder_price")
    cathode_collector_price = get_float(product, "cathode_collector_price_e_kg")

    anode_price = get_float(product, "ano_raw_material_price_€")
    anode_solvent_price = get_float(product, "solvent_price_a")
    anode_additive_price = get_float(product, "additive_price")
    anode_binder_price = get_float(product, "binder_price")
    anode_collector_price = get_float(product, "anode_collector_price_e_kg")

    # Keep DB spelling "separater" if that is the actual column name.
    separator_price = get_float(product, "separater_price_e_kg")
    housing_price = get_float(product, "housing_price")
    electrolyte_price = get_float(product, "electrolyte_material_price_€")
    sealing_price = get_float(product, "sealing_price")

    # Composition validation. Product fields are stored as percentages.
    cathode_composition = (
        get_float(product, "cathode_am_w%")
        + get_float(product, "cathode_additive_w%")
        + get_float(product, "cathode_binder_w%")
    )
    if cathode_composition > 0 and abs(cathode_composition - 100.0) > 1.0:
        raise ValueError(
            "Cathode composition does not sum to 100%. "
            f"Current total: {cathode_composition:.2f}%"
        )

    anode_composition = (
        get_float(product, "anode_am_w%")
        + get_float(product, "anode_additive_w%")
        + get_float(product, "anode_binder_w%")
    )
    if anode_composition > 0 and abs(anode_composition - 100.0) > 1.0:
        raise ValueError(
            "Anode composition does not sum to 100%. "
            f"Current total: {anode_composition:.2f}%"
        )

    # Cathode
    cathode_active_cost = cathode_active_kg * cathode_price
    cathode_solvent_cost = cathode_solvent_kg * cathode_solvent_price
    cathode_additive_cost = cathode_additive_kg * cathode_additive_price
    cathode_binder_cost = cathode_binder_kg * cathode_binder_price
    cathode_collector_cost = cathode_collector_kg * cathode_collector_price

    cathode_total = (
        cathode_active_cost
        + cathode_solvent_cost
        + cathode_additive_cost
        + cathode_binder_cost
        + cathode_collector_cost
    )

    # Anode
    anode_active_cost = anode_active_kg * anode_price
    anode_solvent_cost = anode_solvent_kg * anode_solvent_price
    anode_additive_cost = anode_additive_kg * anode_additive_price
    anode_binder_cost = anode_binder_kg * anode_binder_price
    anode_collector_cost = anode_collector_kg * anode_collector_price

    anode_total = (
        anode_active_cost
        + anode_solvent_cost
        + anode_additive_cost
        + anode_binder_cost
        + anode_collector_cost
    )

    # Assembly
    separator_cost = separator_kg * separator_price
    housing_cost = housing_kg * housing_price
    electrolyte_cost = electrolyte_kg * electrolyte_price

    # Assumes sealing_price is EUR/cell.
    sealing_cost = number_of_cells * sealing_price

    assembly_total = (
        separator_cost
        + housing_cost
        + electrolyte_cost
        + sealing_cost
    )

    total = cathode_total + anode_total + assembly_total

    return {
        "cathode": {
            "active_material": round(cathode_active_cost, 2),
            "solvent": round(cathode_solvent_cost, 2),
            "additive": round(cathode_additive_cost, 2),
            "binder": round(cathode_binder_cost, 2),
            "collector": round(cathode_collector_cost, 2),
            "collector_gross_purchased_kg": round(cathode_collector_kg, 4),
            "collector_trim_kg": round(cathode_trim_kg, 4),
            "collector_trim_purchase_cost_included": round(cathode_trim_kg * cathode_collector_price, 2),
            "total": round(cathode_total, 2),
        },
        "anode": {
            "active_material": round(anode_active_cost, 2),
            "solvent": round(anode_solvent_cost, 2),
            "additive": round(anode_additive_cost, 2),
            "binder": round(anode_binder_cost, 2),
            "collector": round(anode_collector_cost, 2),
            "collector_gross_purchased_kg": round(anode_collector_kg, 4),
            "collector_trim_kg": round(anode_trim_kg, 4),
            "collector_trim_purchase_cost_included": round(anode_trim_kg * anode_collector_price, 2),
            "total": round(anode_total, 2),
        },
        "assembly": {
            "separator": round(separator_cost, 2),
            "housing": round(housing_cost, 2),
            "electrolyte": round(electrolyte_cost, 2),
            "sealing": round(sealing_cost, 2),
            "total": round(assembly_total, 2),
        },
        "total": round(total, 2),
    }
