from models.equipment import EquipmentCreate
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from sqlalchemy import create_engine, text
import os
import numpy as np
import requests

from models import LoginRequest
from models.simulation import SimulationRequest
from uuid import uuid4
from simulation_engine import (

    cells_per_day,

    cells_per_year,

    calculate_process

)
import json
import traceback


# ----------------------------------
# App
# ----------------------------------

app = FastAPI()

# ----------------------------------
# Temporary Simulation Storage
# ----------------------------------

simulation_sessions = {}

# ----------------------------------
# Create Simulation Session
# ----------------------------------

@app.post("/simulation_session")
def create_simulation_session(data: dict):

    session_id = str(uuid4())

    simulation_sessions[session_id] = {

        "plant_code":
            data.get("plant_code"),

        "product_code":
            data.get("product_code"),

        "target_output":
            data.get("target_output"),

        "results":
            []
    }

    return {
        "session_id": session_id
    }


# ----------------------------------
# Save Simulation
# ----------------------------------

@app.post("/save_simulation/{session_id}")
def save_simulation(session_id: str):

    if session_id not in simulation_sessions:

        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    session = simulation_sessions[session_id]

    with engine.begin() as conn:

        conn.execute(

            text("""

                INSERT INTO simulation_results (

                    session_id,

                    plant_code,

                    product_code,

                    target_output,

                    simulation_result

                )

                VALUES (

                    :session_id,

                    :plant_code,

                    :product_code,

                    :target_output,

                    :simulation_result

                )

            """),

            {

                "session_id":
                    session_id,

                "plant_code":
                    session["plant_code"],

                "product_code":
                    session["product_code"],

                "target_output":
                    session["target_output"],

                "simulation_result":
                    json.dumps(
                        session["results"]
                    )

            }

        )

    return {

        "status":
            "saved"

    }

# ----------------------------------
# Deployment verification
# ----------------------------------

# ----------------------------------
# Deployment verification
# ----------------------------------

@app.get("/version")
def version():
    return {
        "version": "render-test-2026-06-03"
    }

@app.get("/render-debug")
def render_debug():
    return {
        "deployment": "fuseki-version-loaded"
    }
@app.get("/deployment-id")
def deployment_id():
    return {
        "deployment": "2026-06-10-debug-01"
    }
# ----------------------------------
# Fuseki debug
# ----------------------------------

@app.get("/fuseki-debug")
def fuseki_debug():

    try:

        response = requests.get(
            "https://gigafactory-fuseki.onrender.com/gigafactory/query",
            timeout=10
        )

        return {
            "status_code": response.status_code,
            "text": response.text[:1000]
        }

    except Exception as e:

        return {
            "error": str(e)
        }
# ----------------------------------
# Security
# ----------------------------------

SECRET_KEY = "gigafactory-secret-key-change-me"

# ----------------------------------
# CORS
# ----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------
# Neon PostgreSQL connection
# ----------------------------------

from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_USPOIom6aK9q@ep-little-cake-a2t42vvz-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

if not DATABASE_URL:
    raise Exception("DATABASE_URL not found")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# ----------------------------------
# Health Check
# ----------------------------------

@app.get("/health")
def health():

    try:

        with engine.connect() as conn:

            conn.execute(
                text("SELECT 1")
            )

        return {
            "status": "healthy"
        }

    except Exception as e:

        return {
            "status": "error",
            "detail": str(e)
        }

# ----------------------------------
# Demo users
# ----------------------------------

users = {
    "admin": "password123"
}

# ----------------------------------
# Login
# ----------------------------------

@app.post("/login")
def login(credentials: LoginRequest):

    if credentials.username not in users:
        raise HTTPException(
            status_code=401,
            detail="Invalid username"
        )

    if credentials.password != users[credentials.username]:
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    token = jwt.encode(
        {"sub": credentials.username},
        SECRET_KEY,
        algorithm="HS256"
    )

    return {
        "token": token
    }


# ----------------------------------
# Existing plot endpoint
# ----------------------------------

@app.get("/dwelling-time")
def get_dwelling_time():

    solid_content = np.linspace(0, 50, 100)

    dwelling_time = 10 - 0.1 * solid_content

    return {
        "x": solid_content.tolist(),
        "y": dwelling_time.tolist()
    }


# ----------------------------------
# PostgreSQL test
# ----------------------------------

@app.get("/db-test")
def db_test():

    if engine is None:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL not configured"
        )

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("SELECT NOW();")
            )

            current_time = result.scalar()

            return {
                "status": "connected",
                "database_time": str(current_time)
            }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ----------------------------------
# Equipment CREATE
# ----------------------------------

@app.post("/equipment")
def create_equipment(equipment: dict):

    columns = ", ".join(equipment.keys())

    values = ", ".join(
        [f":{k}" for k in equipment.keys()]
    )

    sql = f"""
        INSERT INTO equipment
        ({columns})
        VALUES
        ({values})
    """

    with engine.begin() as conn:

        conn.execute(
            text(sql),
            equipment
        )

    return {
        "status": "created"
    }

# ----------------------------------
# Equipment READ
# ----------------------------------

@app.get("/equipment")
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

@app.put("/equipment/{equipment_id}")
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

@app.delete("/equipment/{equipment_id}")
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

@app.get("/equipment/schema")
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
# Equipment Check
# ----------------------------------

@app.get("/equipment/check")
def check_equipment_table():

    if engine is None:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL not configured"
        )

    try:

        with engine.connect() as conn:

            result = conn.execute(text("""
                SELECT column_name,
                       data_type
                FROM information_schema.columns
                WHERE table_name = 'equipment'
                ORDER BY ordinal_position
            """))

            columns = [dict(row._mapping) for row in result]

            return {
                "table_exists": len(columns) > 0,
                "columns": columns
            }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ----------------------------------
# Equipment Options
# ----------------------------------

@app.get("/equipment/options")
def equipment_options():

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT
                        id,
                        technology_name,
                        process,
                        quality_rate
                    FROM equipment
                    ORDER BY technology_name
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
# Product Configuration CREATE
# ----------------------------------

@app.post("/product_configuration")
def create_product_configuration(record: dict):

    columns = ", ".join(record.keys())

    values = ", ".join(
        [f":{k}" for k in record.keys()]
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
        "status": "created"
    }


# ----------------------------------
# Product Configuration UPDATE
# ----------------------------------

@app.put("/product_configuration/{record_id}")
def update_product_configuration(
    record_id: int,
    record: dict
):

    set_clause = ", ".join(
        [f"{k}=:{k}" for k in record.keys()]
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
        "status": "updated"
    }


# ----------------------------------
# Product Configuration READ
# ----------------------------------

@app.get("/product_configuration")
def get_product_configuration():

    try:

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

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ----------------------------------
# Product Configuration DELETE
# ----------------------------------

@app.delete("/product_configuration/{record_id}")
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

@app.get("/product_configuration/schema")
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

@app.get("/product_configuration/check")
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

@app.get("/product_configuration/options")
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
# Product Configuration Options
# ----------------------------------

@app.get("/product_configuration/options")
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

@app.post("/product_material")
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

@app.get("/product_material")
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

@app.put("/product_material/{record_id}")
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

@app.delete("/product_material/{record_id}")
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

@app.get("/product_material/schema")
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

@app.get("/product_material/check")
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

@app.get("/product_material/options")
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

@app.get("/debug-production-columns")
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

@app.post("/production_configuration")
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

@app.put("/production_configuration/{record_id}")
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

@app.get("/production_configuration")
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
# Production Configuration Options
# ----------------------------------

@app.get("/production_configuration/options")
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
# Production Configuration DELETE
# ----------------------------------

@app.delete("/production_configuration/{record_id}")
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

@app.get("/production_configuration/schema")
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

@app.get("/production_configuration/check")
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
# Fuseki test
# ----------------------------------

@app.get("/fuseki-test")
def fuseki_test():

    query = """
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o
    }
    LIMIT 10
    """

    try:

        response = requests.post(
            "https://gigafactory-fuseki.onrender.com/gigafactory/query",
            data={"query": query},
            headers={
                "Accept": "application/sparql-results+json"
            },
            timeout=30
        )

        return {
            "status_code": response.status_code,
            "response": response.json()
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# -------------------------------------------------------
# ROUTE SIMULATION
# -------------------------------------------------------

@app.post("/simulation/run")
def run_simulation(request: dict):

    product_code = request["product_code"]
    plant_code = request["plant_code"]
    route = request["route"]

    with engine.connect() as conn:

        # -------------------------
        # Product configuration
        # -------------------------

        product = conn.execute(
            text("""
                SELECT *
                FROM product_configuration
                WHERE productcode = :product
            """),
            {"product": product_code}
        ).mappings().first()

        if not product:

            raise HTTPException(
                status_code=404,
                detail="Product configuration not found."
            )

        # -------------------------
        # Production configuration
        # -------------------------

        production = conn.execute(
            text("""
                SELECT annual_output
                FROM production_configuration
                WHERE plant_code = :plant
                AND product_code = :product
            """),
            {
                "plant": plant_code,
                "product": product_code
            }
        ).mappings().first()

        if not production:

            raise HTTPException(
                status_code=404,
                detail="Production configuration not found."
            )

    # ---------------------------------------------------
    # Calculate required good cells/day
    # ---------------------------------------------------

    annual_output_gwh = float(production["annual_output"])
    cell_capacity = float(product["cell_capacity_kwh"])

    annual_energy_kwh = annual_output_gwh * 1_000_000

    required_good_cells_year = annual_energy_kwh / cell_capacity
    required_good_cells_day = required_good_cells_year / 365

    required_cells = required_good_cells_day

    simulation = []

    # ---------------------------------------------------
    # Backward calculation
    # ---------------------------------------------------

    for equipment in reversed(route):

        quality = float(equipment["quality_rate"]) / 100

        required_input_cells = required_cells / quality

        category = equipment["process_category"]

        # ---------------------------------------------
        # CELL PROCESS
        # ---------------------------------------------

        if category == "CELL":

            output = required_cells
            input_required = required_input_cells
            unit = "cells/day"

        # ---------------------------------------------
        # CATHODE ROLL
        # ---------------------------------------------

        elif category == "CATHODE_ROLL":

            output = (
                required_cells
                * product["number_of_electrodes_in_cell"]
                * product["cathode_length_mm"]
                / 1000
            )

            output = output / quality

            input_required = output

            unit = "m/day"

        # ---------------------------------------------
        # ANODE ROLL
        # ---------------------------------------------

        elif category == "ANODE_ROLL":

            output = (
                required_cells
                * product["number_of_electrodes_in_cell"]
                * product["anode_length_mm"]
                / 1000
            )

            output = output / quality

            input_required = output

            unit = "m/day"

        # ---------------------------------------------
        # CATHODE MASS
        # ---------------------------------------------

        elif category == "CATHODE_MASS":

            roll_length = (
                required_cells
                * product["number_of_electrodes_in_cell"]
                * product["cathode_length_mm"]
                / 1000
            )

            output = (
                roll_length
                * product["cath_coll_width_m"]
                * product["mass_load_cath_kg_m2"]
            )

            output = output / quality

            input_required = output

            unit = "kg/day"

        # ---------------------------------------------
        # ANODE MASS
        # ---------------------------------------------

        elif category == "ANODE_MASS":

            roll_length = (
                required_cells
                * product["number_of_electrodes_in_cell"]
                * product["anode_length_mm"]
                / 1000
            )

            output = (
                roll_length
                * product["anode_coll_width_m"]
                * product["mass_load_anode_kg_m2"]
            )

            output = output / quality

            input_required = output

            unit = "kg/day"

        else:

            output = required_cells
            input_required = required_input_cells
            unit = "units/day"

        simulation.append({

            "technology_id": equipment["technology_id"],

            "technology_name": equipment["technology_name"],

            "process": equipment["process"],

            "category": category,

            "quality_rate": equipment["quality_rate"],

            "unit": unit,

            "required_output": round(output, 2),

            "required_input": round(input_required, 2)

        })

        required_cells = required_input_cells

    simulation.reverse()

    return {

        "plant_code": plant_code,

        "product_code": product_code,

        "required_good_cells_day": round(required_good_cells_day, 2),

        "simulation": simulation

    }

# ----------------------------------
# Root endpoint
# ----------------------------------

@app.get("/")
def root():

    return {
        "message": "Gigafactory Platform Backend Running",
        "version": "render-test-2026-06-03"
    }
