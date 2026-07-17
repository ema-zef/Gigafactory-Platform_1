from sqlalchemy import create_engine, text
from fastapi import HTTPException
from config import DATABASE_URL

# ----------------------------------
# Equipment Check
# ----------------------------------

def check_equipment_table():

    try:

        with engine.connect() as conn:

            result = conn.execute(text("""

                SELECT column_name,
                       data_type

                FROM information_schema.columns

                WHERE table_name='equipment'

                ORDER BY ordinal_position

            """))

            columns = [

                dict(row._mapping)

                for row in result

            ]

            return {

                "table_exists":

                    len(columns) > 0,

                "columns":

                    columns

            }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )
        
# ----------------------------------
# Equipment READ
# ----------------------------------

def get_equipment():

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT * FROM equipment ORDER BY id")
        )

        return [
            dict(row._mapping)
            for row in result
        ]

# ----------------------------------
# Equipment Update
# ----------------------------------

def update_equipment(
    equipment_id: int,
    equipment: dict
):

    set_clause = ", ".join(
        [f"{k}=:{k}" for k in equipment.keys()]
    )

    sql = f"""
        UPDATE equipment
        SET {set_clause}
        WHERE id=:id
    """

    with engine.begin() as conn:

        conn.execute(
            text(sql),
            {
                **equipment,
                "id": equipment_id
            }
        )

    return {
        "status": "updated"
    }

# ----------------------------------
# Equipment DELETE
# ----------------------------------

def delete_equipment(equipment_id: int):

    with engine.begin() as conn:

        conn.execute(
            text("""
                DELETE FROM equipment
                WHERE id=:id
            """),
            {"id": equipment_id}
        )

    return {
        "status": "deleted"
    }

# ----------------------------------
# Equipment Metadata
# ----------------------------------

def equipment_schema():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_name='equipment'
                ORDER BY ordinal_position
            """)
        )

        return [
            dict(row._mapping)
            for row in result
        ]




# ----------------------------------
# Product Configuration CREATE
# ----------------------------------
 
def insert_product_configuration(record):

    columns = ", ".join(record.keys())

    values = ", ".join(

        f":{k}"

        for k in record.keys()

    )

    sql = f"""

        INSERT INTO product_configuration

        ({columns})

        VALUES

        ({values})

    """

    with engine.begin() as conn:

        conn.execute(

            text(sql),

            record

        )

    return {

        "status":"created"

    }
 
# ----------------------------------
# Product Configuration UPDATE
# ----------------------------------
 
def update_product_configuration(

    record_id,

    record

):

    set_clause = ", ".join(

        f"{k}=:{k}"

        for k in record.keys()

    )

    sql = f"""

        UPDATE product_configuration

        SET {set_clause}

        WHERE id=:id

    """

    with engine.begin() as conn:

        conn.execute(

            text(sql),

            {

                **record,

                "id": record_id

            }

        )

    return {

        "status":"updated"

    }
    
# ----------------------------------
# Product Configuration READ
# ----------------------------------
    
def read_product_configuration():

    with engine.connect() as conn:

        result = conn.execute(

            text("""

                SELECT *

                FROM product_configuration

                ORDER BY id

            """)

        )

        return [

            dict(row._mapping)

            for row in result

        ]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# ----------------------------------
# Product Configuration DELETE
# ----------------------------------

def delete_product_configuration(
    record_id: int
):

    with engine.begin() as conn:

        conn.execute(
            text("""
                DELETE FROM product_configuration
                WHERE id=:id
            """),
            {"id": record_id}
        )

    return {
        "status": "deleted"
    }

# ----------------------------------
# Product Configuration Schema
# ----------------------------------

def product_configuration_schema():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_name='product_configuration'
                ORDER BY ordinal_position
            """)
        )

        return [
            dict(row._mapping)
            for row in result
        ]

# ----------------------------------
# Product Configuration Check
# ----------------------------------

def check_product_configuration():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_name='product_configuration'
                ORDER BY ordinal_position
            """)
        )

        columns = [
            dict(row._mapping)
            for row in result
        ]

        return {
            "table_exists":
                len(columns) > 0,
            "columns":
                columns
        }

# ----------------------------------
# Product Configuration Options
# ----------------------------------

def get_product_configuration_options():

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT DISTINCT productcode
                    FROM product_configuration
                    WHERE productcode IS NOT NULL
                    ORDER BY productcode
                """)
            )

            return [
                row[0]
                for row in result
            ]

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ----------------------------------
# Product Material CREATE
# ----------------------------------

def create_product_material(record: dict):

    columns = ", ".join(record.keys())

    values = ", ".join(
        [f":{k}" for k in record.keys()]
    )

    sql = f"""
        INSERT INTO product_material
        ({columns})
        VALUES
        ({values})
    """

    with engine.begin() as conn:

        conn.execute(
            text(sql),
            record
        )

    return {
        "status": "created"
    }
    
# ----------------------------------
# Product Material READ
# ----------------------------------

def get_product_material():

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT *
                    FROM product_material
                    ORDER BY seq
                """)
            )

            return [
                dict(row._mapping)
                for row in result
            ]

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        
# ----------------------------------
# Product Material UPDATE
# ----------------------------------

def update_product_material(
    record_id: int,
    record: dict
):

    # Prevent updating the primary key
    record.pop("seq", None)

    set_clause = ", ".join(
        [f"{k}=:{k}" for k in record.keys()]
    )

    sql = f"""
        UPDATE product_material
        SET {set_clause}
        WHERE seq = :seq
    """

    with engine.begin() as conn:

        conn.execute(
            text(sql),
            {
                **record,
                "seq": record_id
            }
        )

    return {
        "status": "updated"
    }

# ----------------------------------
# Product Material DELETE
# ----------------------------------

def delete_product_material(record_id: int):

    with engine.begin() as conn:

        conn.execute(
            text("""
                DELETE FROM product_material
                WHERE seq = :seq
            """),
            {"seq": record_id}
        )

    return {
        "status": "deleted"
    }
    
# ----------------------------------
# Product Material Schema
# ----------------------------------

def product_material_schema():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_name='product_material'
                ORDER BY ordinal_position
            """)
        )

        return [
            dict(row._mapping)
            for row in result
        ]
        
# ----------------------------------
# Product Material Check
# ----------------------------------

def check_product_material():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_name='product_material'
                ORDER BY ordinal_position
            """)
        )

        columns = [
            dict(row._mapping)
            for row in result
        ]

        return {
            "table_exists":
                len(columns) > 0,
            "columns":
                columns
        }
        
# ----------------------------------
# Product Material Options
# ----------------------------------

def get_product_material_options():

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT DISTINCT productcode
                    FROM product_material
                    WHERE productcode IS NOT NULL
                    ORDER BY productcode
                """)
            )

            return [
                row[0]
                for row in result
            ]

    except Exception as e:

        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        
# ----------------------------------
# Debug Production Configuration Columns
# ----------------------------------

def debug_production_columns():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='production_configuration'
                ORDER BY ordinal_position
            """)
        )

        return [
            row[0]
            for row in result
        ]
        
# ----------------------------------
# Production Configuration CREATE
# ----------------------------------

def create_production_configuration(
    record: dict
):

    columns = ", ".join(record.keys())

    values = ", ".join(
        [f":{k}" for k in record.keys()]
    )

    sql = f"""
        INSERT INTO production_configuration
        ({columns})
        VALUES
        ({values})
    """

    with engine.begin() as conn:

        conn.execute(
            text(sql),
            record
        )

    return {
        "status": "created"
    }
    
# ----------------------------------
# Production Configuration UPDATE
# ----------------------------------

def update_production_configuration(
    record_id: int,
    data: dict
):

    set_clause = ", ".join(
        [f"{k}=:{k}" for k in data.keys()]
    )

    sql = f"""
        UPDATE production_configuration
        SET {set_clause}
        WHERE id=:id
    """

    with engine.begin() as conn:

        conn.execute(
            text(sql),
            {
                **data,
                "id": record_id
            }
        )

    return {"status": "updated"}
    
# ----------------------------------
# Production Configuration READ
# ----------------------------------

def get_production_configuration():

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT *
                    FROM production_configuration
                    ORDER BY id
                """)
            )

            return [
                dict(row._mapping)
                for row in result
            ]

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        
# ----------------------------------
# Production Configuration DELETE
# ----------------------------------

def delete_production_configuration(
    record_id: int
):

    with engine.begin() as conn:

        conn.execute(
            text("""
                DELETE FROM production_configuration
                WHERE id=:id
            """),
            {"id": record_id}
        )

    return {"status": "deleted"}

# ----------------------------------
# Production Configuration Schema
# ----------------------------------

def production_configuration_schema():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_name='production_configuration'
                ORDER BY ordinal_position
            """)
        )

        return [
            dict(row._mapping)
            for row in result
        ]  

# ----------------------------------
# Production Configuration Check
# ----------------------------------

def check_production_configuration():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_name='production_configuration'
                ORDER BY ordinal_position
            """)
        )

        columns = [
            dict(row._mapping)
            for row in result
        ]

        return {
            "table_exists":
                len(columns) > 0,
            "columns":
                columns
        }
        
# ----------------------------------
# Production Configuration OPTION
# ----------------------------------

def get_production_configuration_options():

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT DISTINCT code
                    FROM production_configuration
                    WHERE code IS NOT NULL
                    AND TRIM(code) <> ''
                    ORDER BY code
                """)
            )

            return [
                row[0]
                for row in result
            ]

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        
# ----------------------------------
# Product Configuration QUERY
# ----------------------------------

def load_product_configuration(product_code):

    with engine.connect() as conn:

        return conn.execute(

            text("""
                SELECT *
                FROM product_configuration
                WHERE productcode = :product
            """),

            {"product": product_code}

        ).mappings().first()
    
# ----------------------------------
# Production Configuration QUERY
# ----------------------------------

def load_production_configuration(plant_code):
    
    with engine.connect() as conn:
    
        return conn.execute(
            text("""
                SELECT
                annual_output_kwh,
                hours_per_shift,
                no_of_shifts_per_day,
                available_time_min,
                electricity_cost_rate_min_eur_per_kwh,
                electricity_cost_rate_max_eur_per_kwh,
                gas_cost_rate_min_eur_per_kwh,
                gas_cost_rate_max_eur_per_kwh,
                floor_space_cost_rate_eur_per_m2,
                elec_ghge_rate,
                gas_ghge_rate,
                operator_rate
                FROM production_configuration
                WHERE code = :plant
            """),
            {
             "plant": plant_code
            }
        ).mappings().first()

# ----------------------------------
# Equipment QUERY
# ----------------------------------

def load_equipment(ids):
    
    with engine.connect() as conn:
        
    return conn.execute(

    text("""
        SELECT
            no_operators_min,
            no_operators_max
        FROM equipment
        WHERE id = :equipment_id
    """),

    {
        "equipment_id": equipment["technology_id"]
    }

).mappings().first()