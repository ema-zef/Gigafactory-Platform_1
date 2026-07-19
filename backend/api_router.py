from fastapi import APIRouter

from routes.auth_routes import router as auth_router
from routes.product_routes import router as product_router
from routes.product_material_routes import router as product_material_router
from routes.production_routes import router as production_router
from routes.equipment_routes import router as equipment_router
from routes.simulation_routes import router as simulation_router
from routes.analytics_routes import router as analytics_router
from routes.system_routes import router as system_router
from routes.debug_routes import router as debug_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(product_router)
api_router.include_router(product_material_router)
api_router.include_router(production_router)
api_router.include_router(equipment_router)
api_router.include_router(simulation_router)
api_router.include_router(analytics_router)
api_router.include_router(system_router)
api_router.include_router(debug_router)


    


    

    
