from fastapi import FastAPI
from src.controllers.container_controller import router as container_router

app = FastAPI()

# Incluindo as rotas do controller
app.include_router(container_router, prefix="/api/v1")
