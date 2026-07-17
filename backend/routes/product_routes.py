from fastapi import APIRouter

router = APIRouter()

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
