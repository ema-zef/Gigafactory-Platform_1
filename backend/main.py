from models.equipment import EquipmentCreate
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from sqlalchemy import create_engine, text
import os
import numpy as np
import requests

from models import LoginRequest

# ----------------------------------
# App
# ----------------------------------

app = FastAPI()

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

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)

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
def create_equipment(equipment: EquipmentCreate):

    if engine is None:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL not configured"
        )

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    INSERT INTO equipment (
                        equipment_name,
                        equipment_type,
                        manufacturer,
                        power_kw,
                        capex_eur,
                        throughput
                    )
                    VALUES (
                        :equipment_name,
                        :equipment_type,
                        :manufacturer,
                        :power_kw,
                        :capex_eur,
                        :throughput
                    )
                """),
                {
                    "equipment_name": equipment.equipment_name,
                    "equipment_type": equipment.equipment_type,
                    "manufacturer": equipment.manufacturer,
                    "power_kw": equipment.power_kw,
                    "capex_eur": equipment.capex_eur,
                    "throughput": equipment.throughput,
                }
            )

        return {
            "status": "success",
            "message": "Equipment created"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ----------------------------------
# Equipment READ
# ----------------------------------

@app.get("/equipment")
def get_equipment():

    if engine is None:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL not configured"
        )

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT
                        equipment_id,
                        equipment_name,
                        equipment_type,
                        manufacturer,
                        power_kw,
                        capex_eur,
                        throughput
                    FROM equipment
                    ORDER BY equipment_name
                """)
            )

            rows = result.mappings().all()

            return rows

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# ----------------------------------
# Equipment DELETE
# ----------------------------------

@app.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: int):

    if engine is None:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL not configured"
        )

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    DELETE FROM equipment
                    WHERE equipment_id = :id
                """),
                {"id": equipment_id}
            )

        return {
            "status": "success"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
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

# ----------------------------------
# Root endpoint
# ----------------------------------

@app.get("/")
def root():

    return {
        "message": "Gigafactory Platform Backend Running",
        "version": "render-test-2026-06-03"
    }
