from fastapi import HTTPException
from uuid import uuid4
from models.equipment import EquipmentCreate
from models import LoginRequest
from models.simulation import SimulationRequest

# ----------------------------------
# Create Simulation Session
# ----------------------------------

@app.post("/simulation_session")
def create_simulation_session(data: dict):

    return {
        "session_id": session_id
    }

# ----------------------------------
# Save Simulation
# ----------------------------------

@app.post("/save_simulation/{session_id}")
def save_simulation(session_id: str):

    return {

        "status":
            "saved"

    }
    
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
# Root
# ----------------------------------

@app.get("/")
def root():

    return {

        "message":"Gigafactory Platform Backend Running",

        "version":"render-test-2026-06-03"

    }
