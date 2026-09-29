from fastapi import APIRouter, Depends
from auth import current_user
from routes.auth_routes import router as auth_router
from routes.owned_data_routes import router as data_router
from routes.simulation_routes import router as simulation_router
from routes.scenario_routes import router as scenario_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(data_router)
api_router.include_router(simulation_router)
api_router.include_router(scenario_router)
# IMPORTANT: legacy analytics/system/debug routers are deliberately NOT mounted.
# Their raw database access must be audited and scoped before external deployment.
