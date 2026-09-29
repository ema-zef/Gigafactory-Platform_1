"""Simulation inputs are fetched only by authorized, unique IDs."""
from fastapi import HTTPException
from access import record_for, visible_rows


def inputs(request, user):
    product = record_for('product_configuration', request.product_id, user)
    production = record_for('production_configuration', request.plant_id, user)
    if product.get('productcode') != request.product_code or production.get('code') != request.plant_code:
        raise HTTPException(422, 'Selected product or plant does not match its ID')
    material = None
    if request.product_material_id:
        material = record_for('product_material', request.product_material_id, user)
        if material['productcode'] != request.product_code:
            raise HTTPException(422, 'Selected material does not match the product')
    else:
        matches = [m for m in visible_rows('product_material', user) if m.get('productcode') == request.product_code]
        if len(matches) != 1:
            raise HTTPException(422, 'Select a unique product material record for this product')
        material = matches[0]
    ids = {step.technology_id for branch in (request.cathode_route, request.anode_route, request.assembly_route) for step in branch}
    equipment = {i: record_for('equipment', i, user) for i in ids}
    return product, material, production, equipment
