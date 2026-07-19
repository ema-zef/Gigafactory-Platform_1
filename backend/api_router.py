from fastapi import APIRouter

from routes.equipment_routes import router as equipment_router
from routes.product_routes import router as product_router
from routes.production_routes import router as production_router
from routes.simulation_routes import router as simulation_router
from routes.debug_routes import router as debug_router
from routes.product_material_routes import router as product_material_router

api_router = APIRouter()

api_router.include_router(equipment_router)
api_router.include_router(product_router)
api_router.include_router(production_router)
api_router.include_router(simulation_router)
api_router.include_router(debug_router)
api_router.include_router(product_material_router)


    


    

    
