from typing import Optional, List
from src.infrastructure.database.connection import db
from src.domain.container import Container
from src.mappers.container_mapper import ContainerMapper, get_container_mapper
from src.enums.Shipowners import Shipowners
from src.enums.ShippingStatus import ShippingStatus
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
        container = await self.collection.find_one({
            "number": container_number,
            "shipping_status": ShippingStatus.PROCESSING.value
        })  
        if container is None:
            return None
        return self.container_mapper.from_dict_to_domain(container)
    
    async def update(self, container: Container) -> None:
        if container._id is None:
            raise ValueError("O container precisa ter um _id para ser atualizado.")
        
        container_dict = self.container_mapper.from_domain_to_dict(container)

        await self.collection.replace_one(
            {"_id": ObjectId(container._id)},
            container_dict
        )
    
    async def get_all_by_number(self, container_number: str) -> List[Container]:
        cursor = self.collection.find({"number": container_number})
        containers = []
        async for document in cursor:
            container = self.container_mapper.from_dict_to_domain(document)
            containers.append(container)
        return containers

    async def find_all_for_grid(self) -> List[dict]:
        projection = {
            "_id": 1,
            "number": 1,
            "master_bill_of_lading_number": 1,
            "booking_number": 1,
            "events": 1,
            "search_logs": 1,
            "shipowner":1,
            "shipping_status": 1

        }
        cursor = self.collection.find({}, projection)
        return await cursor.to_list(length=None)
    
    async def get_by_id(self, id: str) -> Optional[dict]:
        container = await self.collection.find_one({
            "_id": ObjectId(id),
        })  
        if container is None:
            return None
        return self.container_mapper.from_dict_to_domain(container)
    
def get_container_repository(
        container_mapper: ContainerMapper = Depends(get_container_mapper)
):
    return ContainerRepository(container_mapper)
