from fastapi import APIRouter, HTTPException, Depends, Query, status
from src.models.container_create import ContainerCreate
from src.models.container_update import ContainerUpdate
from src.services.container_service import ContainerService, get_container_service
from typing import List, Optional
from src.models.grid_paginated_response import GridPaginatedResponse

router = APIRouter()

@router.post("/containers")
async def create_container(container: ContainerCreate, service: ContainerService = Depends(get_container_service)):
    try:
        result = await service.register_container(container)
        return {"message": "Container registered", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@router.get("/containers/{id}")
async def get_container(id: str, service: ContainerService = Depends(get_container_service)):
    container = await service.get_container_by_id(id)
    if container:
        return {"message": "Container encontrado", "data": container}
    return {"message": "Container não encontrado", "data": None}

@router.get("/containers", response_model=GridPaginatedResponse)
async def get_container_grid(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    container_service: ContainerService = Depends(get_container_service)
):
    return await container_service.get_paginated_grid(search, page, page_size)

@router.delete("/containers/{id}", status_code=status.HTTP_200_OK)
async def delete_container(id: str, service: ContainerService = Depends(get_container_service)):
    try:
        result = await service.delete_container_by_id(id)
        return {"message": result["message"], "container_id": result["container_id"]}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")
    
@router.put("/containers/{id}", status_code=status.HTTP_200_OK)
async def update_container(id: str, container_update: ContainerUpdate, service: ContainerService = Depends(get_container_service)):
    try:
        if container_update.id != id:
            raise HTTPException(
                status_code=400,
                detail=f"O ID da rota ('{id}') é diferente do ID do corpo da requisição ('{container_update.id}')."
            )
        result = await service.update_container(container_update.id, container_update.booking_number, container_update.house_bill_of_lading_number)
        return {"message": result["message"], "container_id": result["container_id"]}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")