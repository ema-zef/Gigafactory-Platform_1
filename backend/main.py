from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes import router

# ----------------------------------
# App
# ----------------------------------

app = FastAPI()

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



























   
        
        
       
        
        





    
