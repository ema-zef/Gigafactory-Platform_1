from fastapi import APIRouter

router = APIRouter()

from database import (
    create_production_configuration,
    update_production_configuration,
    read_production_configuration,
    delete_production_configuration_db,
    get_production_configuration_schema,
    check_production_configuration_db,
    read_production_configuration_options,
)

import uuid

# ----------------------------------
# Product Configuration CREATE
# ----------------------------------

@router.post("/product_configuration")
def create_product(record: dict):

    return insert_product_configuration(record)
    
# ----------------------------------
# Product Configuration UPDATE
# ----------------------------------
 
@router.put("/product_configuration/{record_id}")
def update_product(

    record_id: int,

    record: dict

):

    return update_product_configuration(

        record_id,

        record

    )
    
# ----------------------------------
# Product Configuration READ
# ----------------------------------
    
@router.get("/product_configuration")
def get_products():

    return read_product_configuration()
    
# ----------------------------------
# Product Configuration DELETE
# ----------------------------------

@router.delete("/product_configuration/{record_id}")
def delete_product(

    record_id: int

):

    return delete_product_configuration(

        record_id

    )

# ----------------------------------
# Product Configuration Schema
# ----------------------------------
    
@router.get("/product_configuration/schema")
def product_schema():

    return get_product_configuration_schema()

# ----------------------------------
# Product Configuration Check
# ----------------------------------

@router.get("/product_configuration/check")
def product_check():

    return check_product_configuration()
     
# ----------------------------------
# Product Configuration Options
# ----------------------------------

@router.get("/product_configuration/options")
def product_options():

    return get_product_configuration_options()

# ----------------------------------
# Create Simulation Session
# ----------------------------------

@router.post("/simulation_session")
def create_simulation_session(data: dict):

    session_id = str(uuid.uuid4())

    return {
        "session_id": session_id
    }

# ----------------------------------
# Save Simulation
# ----------------------------------

@router.post("/save_simulation/{session_id}")
def save_simulation(session_id: str):

    return {

        "status":
            "saved"

    }
    
@router.post("/simulation/run")
def run_simulation(data: dict):

    # Run your simulation here

    return {
        "status": "success",
        "result": {}
    }