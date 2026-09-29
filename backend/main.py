import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_router import api_router
from auth import secret_key

secret_key()  # Fail startup if the signing secret is missing or weak.
app = FastAPI(docs_url=None if os.getenv('APP_ENV') == 'production' else '/docs',
              redoc_url=None if os.getenv('APP_ENV') == 'production' else '/redoc')
origins = [origin.strip() for origin in os.getenv('APP_ALLOWED_ORIGINS','').split(',') if origin.strip()]
if not origins:
    raise RuntimeError('Set APP_ALLOWED_ORIGINS to your exact frontend origin(s)')
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False,
                   allow_methods=['GET','POST','PUT','DELETE'],allow_headers=['Authorization','Content-Type'])

@app.get('/health')
def health():
    return {'status':'ok'}

app.include_router(api_router)
