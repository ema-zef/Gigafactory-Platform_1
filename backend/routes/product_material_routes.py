from fastapi import APIRouter

from database import (
    create_product_material,
    update_product_material,
    get_product_material,
    delete_product_material,
    product_material_schema,
    check_product_material,
    get_product_material_options,
)

router = APIRouter()

# ----------------------------------
# Product Material CREATE
# ----------------------------------

@router.post("/product_material")
def create_product_material(record: dict):

    return insert_product_material(record)
    
# ----------------------------------
# Product Material READ
# ----------------------------------  
  
@router.get("/product_material")
def get_product_material():

    return read_product_material()
    
  # ----------------------------------
# Product Material UPDATE
# ----------------------------------  

@router.put("/product_material/{record_id}")
def update_product_material(

    record_id: int,

    record: dict

):

    return update_product_material_db(

        record_id,

        record

    )
    
# ----------------------------------
# Product Material DELETE
# ----------------------------------

@router.delete("/product_material/{record_id}")
def delete_product_material(

    record_id: int

):

    return delete_product_material_db(

        record_id

    )
    
# ----------------------------------
# Product Material Schema
# ----------------------------------

@router.get("/product_material/schema")
def product_material_schema():

    return get_product_material_schema()
    
# ----------------------------------
# Product Material Check
# ----------------------------------

@router.get("/product_material/check")
def product_material_check():

    return check_product_material()
    
# ----------------------------------
# Product Material Options
# ----------------------------------
    
@router.get("/product_material/options")
def product_material_options():

    return get_product_material_options()
    
