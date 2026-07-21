from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.simulation_routes import router as simulation_router

app.include_router(simulation_router)

from api_router import api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)



























   
        
        
       
        
        





    
