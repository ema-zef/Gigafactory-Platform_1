from fastapi import APIRouter
from database import check_equipment_table

from database import (
    insert_equipment,
    update_equipment,
    read_equipment,
    delete_equipment,
    get_equipment_schema,
    check_equipment_table,
    get_equipment_options,
)

router = APIRouter()

from database import check_equipment_table

# ----------------------------------
# Equipment Check
# ----------------------------------

@router.get("/equipment/check")
def equipment_check():

    return check_equipment_table()
    
# ----------------------------------
# Equipment READ
# ----------------------------------

@router.get("/equipment")
def get_equipment():

    return read_equipment()
    
# ----------------------------------
# Equipment Update
# ----------------------------------
    
@router.put("/equipment/{equipment_id}")
def update_equipment(

    equipment_id: int,

    equipment: dict

):

    return update_equipment_db(

        equipment_id,

        equipment

    )
    
# ----------------------------------
# Equipment DELETE
# ----------------------------------

@router.delete("/equipment/{equipment_id}")
def delete_equipment(

    equipment_id: int

):

    return delete_equipment_db(

        equipment_id

    )
    
# ----------------------------------
# Equipment Metadata
# ----------------------------------

@router.get("/equipment/schema")
def equipment_schema():

    return get_equipment_schema()