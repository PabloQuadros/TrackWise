from typing import Optional
from src.infrastructure.database.connection import db
from src.domain.container import Container
from src.mappers.container_mapper import ContainerMapper, get_container_mapper
from fastapi import Depends

class ContainerRepository:
    def __init__(self, container_mapper: ContainerMapper):
        self.collection = db["containers"]
        self.container_mapper = container_mapper

    async def save(self, container: Container) -> None:
        container_dict = self.container_mapper.from_domain_to_dict(container)
        await self.collection.insert_one(container_dict)
        print("Container salvo com sucesso!")

    async def get_by_number(self, container_number: str) -> Optional[dict]:
        return await self.collection.find_one({"number": container_number})
    
def get_container_repository(
        container_mapper: ContainerMapper = Depends(get_container_mapper)
):
    return ContainerRepository(container_mapper)
