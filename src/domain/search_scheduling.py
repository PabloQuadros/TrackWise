from datetime import time
from typing import List, Optional

class ContainerSchedule:
    def __init__(self, container_number: str, search_time: time):
        self.container_number = container_number
        self.search_time = search_time

class SearchScheduling:
    def __init__(self, start_search_time: time, end_search_time: time, containers: List[ContainerSchedule] = None, _id: Optional[str] = None):
        self.start_search_time = start_search_time
        self.end_search_time = end_search_time
        self.containers: List[ContainerSchedule] = containers if containers is not None else []
        self._id = _id or None

    def add_container_schedule(self, container_schedule: ContainerSchedule):
        self.containers.append(container_schedule)

    def get_all_search_times(self) -> List[time]:
        return sorted([c.search_time for c in self.containers])
    
    def remove_container_by_number(self, container_number: str) -> bool:
        original_length = len(self.containers)
        self.containers = [c for c in self.containers if c.container_number != container_number]
        return len(self.containers) < original_length
