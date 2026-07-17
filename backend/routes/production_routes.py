# ----------------------------------
# Debug Production Configuration Columns
# ----------------------------------

@router.get("/debug-production-columns")
def debug_production_columns():

    return debug_production_columns_db()


# ----------------------------------
# Production Configuration CREATE
# ----------------------------------

@router.post("/production_configuration")
def create_production_configuration(record: dict):

    return insert_production_configuration(record)
    
# ----------------------------------
# Production Configuration UPDATE
# ----------------------------------
 
@router.put("/production_configuration/{record_id}")
def update_production_configuration(

    record_id: int,

    data: dict

):

    return update_production_configuration_db(

        record_id,

        data

    )
    
# ----------------------------------
# Production Configuration READ
# ----------------------------------
    
@router.get("/production_configuration")
def get_production_configuration():

    return read_production_configuration()
    
# ----------------------------------
# Production Configuration DELETE
# ----------------------------------

@router.delete("/production_configuration/{record_id}")
def delete_production_configuration(

    record_id: int

):

    return delete_production_configuration_db(

        record_id

    )

# ----------------------------------
# Production Configuration Schema
# ----------------------------------
    
@router.get("/production_configuration/schema")
def production_configuration_schema():

    return get_production_configuration_schema()

# ----------------------------------
# Production Configuration Check
# ----------------------------------

@router.get("/production_configuration/check")
def check_production_configuration():

    return check_production_configuration_db()
     
# ----------------------------------
# Production Configuration Options
# ----------------------------------

@router.get("/production_configuration/options")
def get_production_configuration_options():

    return production_configuration_options()
