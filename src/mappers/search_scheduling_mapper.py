from datetime import datetime
from src.domain.search_scheduling import SearchScheduling
from src.domain.search_scheduling import ContainerSchedule
from bson import ObjectId

class SearchSchedulingMapper:
    
    def from_db_to_domain(self, doc) -> SearchScheduling:
        container_data = [
            ContainerSchedule(
                container_number=entry["container_number"],
                search_time=datetime.strptime(entry["search_time"], "%H:%M:%S").time()
            )
            for entry in doc.get("containers", [])
        ]
        _id=str(doc.get("_id")) if doc.get("_id") else None
        start_time = datetime.strptime(doc["start_search_time"], "%H:%M:%S").time()
        end_time = datetime.strptime(doc["end_search_time"], "%H:%M:%S").time()

        return SearchScheduling(containers=container_data, start_search_time=start_time, end_search_time=end_time, _id=_id)
    
    def from_domain_to_db(self, scheduling: SearchScheduling) -> dict:
        container_data = [
            {
                "container_number": cs.container_number,
                "search_time": cs.search_time.strftime("%H:%M:%S")
            }
            for cs in scheduling.containers
        ]
        data = {
            "containers": container_data,
            "start_search_time": scheduling.start_search_time.strftime("%H:%M:%S"),
            "end_search_time": scheduling.end_search_time.strftime("%H:%M:%S")
        }

        if scheduling._id is not None:
            data["_id"] = ObjectId(scheduling._id)

        return  data
def get_search_scheduling_mapper():
    return SearchSchedulingMapper()