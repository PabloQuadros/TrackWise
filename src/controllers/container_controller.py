from fastapi import APIRouter, HTTPException, Depends
from src.models.container_create import ContainerCreate
from src.services.container_service import ContainerService, get_container_service

router = APIRouter()

@router.post("/containers")
def create_container(container: ContainerCreate, service: ContainerService = Depends(get_container_service)):
    try:
        result = service.register_container(container)
        return {"message": "Container registered", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/containers/{container_number}")
async def get_container(container_number: str, service: ContainerService = Depends(get_container_service)):
    container = service.find_by_container_number(container_number)
    if container:
        return {"message": "Container encontrado", "data": container}
    return {"message": "Container não encontrado", "data": None}

@router.get("/test")
def read_test():
    return {"message": "Teste de rota bem-sucedido!"}