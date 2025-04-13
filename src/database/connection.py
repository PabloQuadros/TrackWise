import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/")
DATABASE_NAME = "track_wise"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
try:
    client = MongoClient(MONGO_URI)
    # Testa a conexão com o MongoDB
    client.admin.command('ping')
    print("Conexão com o MongoDB estabelecida com sucesso!")
except Exception as e:
    print(f"Erro ao conectar ao MongoDB: {e}")