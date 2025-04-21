import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/")
DATABASE_NAME = "track_wise"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
