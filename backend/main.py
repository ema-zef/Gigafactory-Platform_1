from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from sqlalchemy import create_engine, text
import os
import numpy as np
import requests

@app.get("/fuseki-test")
def fuseki_test():

    query = """
    SELECT * WHERE {
        ?s ?p ?o
    }
    LIMIT 10
    """

    response = requests.post(
        "https://gigafactory-fuseki.onrender.com/gigafactory/query",
        data={"query": query}
    )

    return response.json()
from models import LoginRequest

SECRET_KEY = "gigafactory-secret-key-change-me"

print("***** LOADED MAIN.PY WITH VERSION ENDPOINT *****")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi import FastAPI, HTTPException

print("====================================")
print("MAIN.PY LOADED")
print("VERSION 2025-06-04-01")
print("====================================")

from fastapi.middleware.cors import CORSMiddleware
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
# Root endpoint
# ----------------------------------

@app.get("/")
def home():

    return {
        "message": "Gigafactory Platform Backend Running",
        "database_configured": engine is not None
    }

# ----------------------------------
# Health check
# ----------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }

# ----------------------------------
# Version check
# ----------------------------------

@app.get("/version")
def version():

    return {
        "version": "render-test-2026-06-03"
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
# Neon connection test
# ----------------------------------

@app.get("/db-test")
# ----------------------------------
# Fuseki connection test
# ----------------------------------

@app.get("/fuseki-test")
def fuseki_test():

    query = """
    SELECT * WHERE {
        ?s ?p ?o
    }
    LIMIT 10
    """

    try:

        response = requests.post(
            "https://gigafactory-fuseki.onrender.com/gigafactory/query",
            data={"query": query},
            timeout=30
        )

        return {
            "status": "connected",
            "response": response.text
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

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