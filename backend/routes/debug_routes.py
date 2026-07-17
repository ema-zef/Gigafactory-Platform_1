from fastapi import APIRouter

router = APIRouter()

# ----------------------------------
# Fuseki test
# ----------------------------------

@router.get("/fuseki-test")
def fuseki_test():

    return fuseki_test_connection()

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
        


