import os
from dotenv import load_dotenv

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# ----------------------------------
# Security
# ----------------------------------

SECRET_KEY = "gigafactory-secret-key-change-me"

# ----------------------------------
# Neon PostgreSQL connection
# ----------------------------------


load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_USPOIom6aK9q@ep-little-cake-a2t42vvz-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

if not DATABASE_URL:
    raise Exception("DATABASE_URL not found")



