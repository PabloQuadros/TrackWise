from src.domain.container import Container
from src.models.container_create import ContainerCreate
from src.repositories.container_repository import ContainerRepository, get_container_repository
from src.mappers.container_mapper import ContainerMapper, get_container_mapper
from typing import Optional
from fastapi import Depends


class ContainerService:
    def __init__(self, repository: ContainerRepository, container_mapper: ContainerMapper):
        self.repository = repository
        self.container_mapper = container_mapper

    def register_container(self, container_data: ContainerCreate) -> dict:
        # Verifica se já existe o container no banco
        existing = self.repository.get_by_number(container_data.container_number)
        if existing:
            return {"message": "Container já está registrado!", "data": existing}

        # Salva o novo container
        self.repository.save(self.container_mapper.to_container_domain_model(container_data))
        return {"message": "Container registrado com sucesso!", "data": container_data.dict()}

    def find_by_container_number(self, container_number: str) -> Optional[dict]:
        container_data = self.repository.get_by_number(container_number)
        if container_data:
            return self.container_mapper.from_dict_to_view(container_data)
        return None


def get_container_service(
    repository: ContainerRepository = Depends(get_container_repository), 
    container_mapper: ContainerMapper = Depends(get_container_mapper)
) -> ContainerService:
    return ContainerService(repository, container_mapper)