from typing import Optional, List
from src.infrastructure.database.connection import db
from src.domain.container import Container
from src.mappers.container_mapper import ContainerMapper, get_container_mapper
from fastapi import Depends
from bson import ObjectId

class ContainerRepository:
    def __init__(self, container_mapper: ContainerMapper):
        self.collection = db["containers"]
        self.container_mapper = container_mapper

    async def save(self, container: Container) -> None:
        container_dict = self.container_mapper.from_domain_to_dict(container)
        await self.collection.insert_one(container_dict)
        print("Container salvo com sucesso!")

    async def get_by_number(self, container_number: str) -> Optional[dict]:
        container = await self.collection.find_one({"number": container_number})
        if container is None:
            return None
        return self.container_mapper.from_dict_to_domain(container)
    
    async def update(self, container: Container) -> None:
        if container._id is None:
            raise ValueError("O container precisa ter um _id para ser atualizado.")
        
        container_dict = self.container_mapper.from_domain_to_dict(container)

        result = await self.collection.replace_one(
            {"_id": ObjectId(container._id)},
            container_dict
        )

    async def find_all_for_grid(self) -> List[dict]:
        projection = {
            "_id": 1,
            "number": 1,
            "bill_of_lading_number": 1,
            "booking_number": 1,
            "events": 1,
            "search_logs": 1
        }
        cursor = self.collection.find({}, projection)
        return await cursor.to_list(length=None)
    
def get_container_repository(
        container_mapper: ContainerMapper = Depends(get_container_mapper)
):
    return ContainerRepository(container_mapper)
