from src.infrastructure.database.connection import db
from src.domain.search_scheduling import SearchScheduling
from src.mappers.search_scheduling_mapper import SearchSchedulingMapper, get_search_scheduling_mapper
from fastapi import Depends

class SearchSchedulingRepository:
    def __init__(self, search_scheduling_mapper: SearchSchedulingMapper):
        self.collection = db["search_scheduling"]
        self.mapper = search_scheduling_mapper

    def save(self, scheduling: SearchScheduling) -> None:

        doc = self.mapper.to_db(scheduling)
        self.collection.update_one(
            filter={},
            update={"$set": doc},
            upsert=True
        )
    
    def get(self) -> SearchScheduling:
        doc = self.collection.find_one()

        if not doc:
            return None

        return self.mapper.to_domain(doc)

def get_search_scheduling_repository(
    search_scheduling_mapper: SearchSchedulingMapper = Depends(get_search_scheduling_mapper)
) -> SearchSchedulingRepository:
    return SearchSchedulingRepository(search_scheduling_mapper)