from fastapi import APIRouter

router = APIRouter()

# ----------------------------------
# Health Check
# ----------------------------------

@router.get("/health")
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
# PostgreSQL test
# ----------------------------------

@router.get("/db-test")
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

@router.get("/")
def root():

    return {

        "message":"Gigafactory Platform Backend Running",

        "version":"render-test-2026-06-03"

    }
