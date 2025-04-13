from src.domain.container import Container
from src.models.container_create import ContainerCreate
from src.repositories.container_repository import ContainerRepository, get_container_repository
from typing import Optional
from fastapi import Depends


class ContainerService:
    def __init__(self, repository: ContainerRepository):
        self.repository = repository

    def register_container(self, container_data: ContainerCreate) -> dict:
        # Verifica se já existe o container no banco
        existing = self.repository.get_by_number(container_data.container_number)
        if existing:
            return {"message": "Container já está registrado!", "data": existing}

        # Salva o novo container
        self.repository.save(to_container_domain_model(container_data))
        return {"message": "Container registrado com sucesso!", "data": container_data.dict()}

    def find_by_container_number(self, container_number: str) -> Optional[dict]:
        return self.repository.get_by_number(container_number)
    

def to_container_domain_model(create_model: ContainerCreate) -> Container:
    return Container(
        number=create_model.container_number,
        bill_of_lading_number="",
        shipped_from="",
        shipped_to="",
        port_of_load="",
        port_of_discharge="",
        events=[]
)


def get_container_service(
    repository: ContainerRepository = Depends(get_container_repository)
) -> ContainerService:
    return ContainerService(repository)