from datetime import datetime
from src.domain.search_scheduling import SearchScheduling
from src.domain.search_scheduling import ContainerSchedule

class SearchSchedulingMapper:
    
    @staticmethod
    def from_db_to_domain(doc) -> SearchScheduling:
        container_data = [
            (entry["container_number"], datetime.strptime(entry["search_time"], "%H:%M:%S").time())
            for entry in doc.get("containers", [])
        ]

        start_time = datetime.strptime(doc["start_search_time"], "%H:%M:%S").time()
        end_time = datetime.strptime(doc["end_search_time"], "%H:%M:%S").time()

        return SearchScheduling(container=container_data, start_search_time=start_time, end_search_time=end_time)
    
    @staticmethod
    def from_domain_to_db(scheduling: SearchScheduling) -> dict:
        container_data = [
            {
                "container_number": number,
                "search_time": search_time.strftime("%H:%M:%S")
            }
            for number, search_time in scheduling.container
        ]

        return {
            "containers": container_data,
            "start_search_time": scheduling.start_search_time.strftime("%H:%M:%S"),
            "end_search_time": scheduling.end_search_time.strftime("%H:%M:%S")
        }

def get_search_scheduling_mapper():
    return SearchSchedulingMapper()