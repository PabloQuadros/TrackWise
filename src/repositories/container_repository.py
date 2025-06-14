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
    
    async def update(self, container: Container) -> bool:
        if container._id is None:
            raise ValueError("O container precisa ter um _id para ser atualizado.")
        
        container_dict = self.container_mapper.from_domain_to_dict(container)

        result = await self.collection.replace_one(
            {"_id": ObjectId(container._id)},
            container_dict
        )

        return result.modified_count > 0
    
    async def get_all_by_number(self, container_number: str) -> List[Container]:
        cursor = self.collection.find({"number": container_number})
        containers = []
        async for document in cursor:
            container = self.container_mapper.from_dict_to_domain(document)
            containers.append(container)
        return containers

    async def find_all_for_grid(
        self,
        search: Optional[str],
        page: int,
        page_size: int
    ) -> List[dict]:
        query = {}

        if search:
            query["number"] = {"$regex": search, "$options": "i"}

        projection = {
            "_id": 1,
            "number": 1,
            "master_bill_of_lading_number": 1,
            "booking_number": 1,
            "events": 1,
            "search_logs": 1,
            "shipowner": 1,
            "shipping_status": 1
        }

        skip = (page - 1) * page_size

        cursor = self.collection.find(query, projection).skip(skip).limit(page_size)
        return await cursor.to_list(length=page_size)
    
    async def get_by_id(self, id: str) -> Optional[dict]:
        container = await self.collection.find_one({
            "_id": ObjectId(id),
        })  
        if container is None:
            return None
        return self.container_mapper.from_dict_to_domain(container)
    
    async def count_all_for_grid(self, search: Optional[str]) -> int:
        query = {}
        if search:
            query["number"] = {"$regex": search, "$options": "i"}
        return await self.collection.count_documents(query)
    
    async def delete_by_id(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count == 1

    
def get_container_repository(
        container_mapper: ContainerMapper = Depends(get_container_mapper)
):
    return ContainerRepository(container_mapper)
