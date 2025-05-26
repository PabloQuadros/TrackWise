from src.infrastructure.database.connection import db
from src.domain.search_scheduling import SearchScheduling
from src.mappers.search_scheduling_mapper import SearchSchedulingMapper, get_search_scheduling_mapper
from fastapi import Depends
from bson import ObjectId

class SearchSchedulingRepository:
    def __init__(self, search_scheduling_mapper: SearchSchedulingMapper):
        self.collection = db["search_scheduling"]
        self.mapper = search_scheduling_mapper

    async def save(self, scheduling: SearchScheduling) -> None:
        doc = self.mapper.from_domain_to_db(scheduling)
        await self.collection.update_one(
            filter={},
            update={"$set": doc},
            upsert=True
        )
    
    async def get(self) -> SearchScheduling:
        doc = await self.collection.find_one()

        if not doc:
            return None

        return self.mapper.from_db_to_domain(doc)
    
    async def update(self, scheduling: SearchScheduling) -> None:     
        scheduling_dict = self.mapper.from_domain_to_db(scheduling)
        await self.collection.replace_one(
            {"_id": ObjectId(scheduling._id)},
            scheduling_dict
        )

def get_search_scheduling_repository(
    search_scheduling_mapper: SearchSchedulingMapper = Depends(get_search_scheduling_mapper)
) -> SearchSchedulingRepository:
    return SearchSchedulingRepository(search_scheduling_mapper)