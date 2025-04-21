from src.domain.container import Container
from src.models.container_create import ContainerCreate
from src.repositories.container_repository import ContainerRepository, get_container_repository
from src.mappers.container_mapper import ContainerMapper, get_container_mapper
from src.services.msc_service import MscService, get_msc_service
from src.services.search_scheduling_service import SearchSchedulingService, get_search_scheduling_service
from typing import Optional
from fastapi import Depends, HTTPException


class ContainerService:
    def __init__(self, repository: ContainerRepository, container_mapper: ContainerMapper, msc_service: MscService, search_scheduling_service: SearchSchedulingService):
        self.repository = repository
        self.container_mapper = container_mapper
        self.msc_service = msc_service
        self.search_scheduling_service = search_scheduling_service

    async def register_container(self, container_data: ContainerCreate) -> dict:
        # Verifica se já existe o container no banco
        existing_on_database = await self.repository.get_by_number(container_data.number)
        if existing_on_database:
            return {"message": "Container já está registrado!"}
        #Verifica se o container existe no site do armador
        existing_on_shipowner = await self.msc_service.validate_container_existence(container_data.number)
        if existing_on_shipowner.get("IsSuccess") is False:
            raise HTTPException(status_code=404, detail="O número do container informado não foi localizado no site do armador")

        #Mapeia da response do armador para a entidade de dominio
        container = self.container_mapper.from_api_response_to_domain_model(existing_on_shipowner)
        #Completa com as informações da requisição
        container = self.container_mapper.complete_container_model_with_request_data(container, container_data)
        self.repository.save(container)
        self.search_scheduling_service.add_container_schedule(container.number)
        return {"message": "Container registrado com sucesso!", "data": container_data.dict()}

    async def find_by_container_number(self, container_number: str) -> Optional[dict]:
        container_data = await self.repository.get_by_number(container_number)
        if container_data:
            return self.container_mapper.from_dict_to_view(container_data)
        return None       


def get_container_service(
    repository: ContainerRepository = Depends(get_container_repository), 
    container_mapper: ContainerMapper = Depends(get_container_mapper),
    msc_service: MscService = Depends(get_msc_service),
    search_scheduling_service: SearchSchedulingService = Depends(get_search_scheduling_service)
) -> ContainerService:
    return ContainerService(repository, container_mapper, msc_service, search_scheduling_service)