from typing import List, Optional
from src.enums.SearchStatus import SearchStatus
from datetime import datetime

class SearchLog:
    def __init__(self, timestamp: datetime, status: SearchStatus):
        self.timestamp = timestamp
        self.status = status

class Event:
    def __init__(
        self,
        order: int,
        date: str,
        location: str,
        un_location_code: str,
        description: str,
        detail: List[str]
    ):
        self.order = order
        self.date = date
        self.location = location
        self.un_location_code = un_location_code
        self.description = description
        self.detail = detail
    
class Container:
    def __init__(
        self,
        number: str,
        bill_of_lading_number: str,
        shipped_from: str,
        shipped_to: str,
        port_of_load: str,
        port_of_discharge: str,
        events: Optional[List[Event]] = None,
        booking_number: Optional[str] = None,
        search_logs: Optional[List[SearchLog]] = None
    ):
        self.number = number
        self.bill_of_lading_number = bill_of_lading_number
        self.shipped_from = shipped_from
        self.shipped_to = shipped_to
        self.port_of_load = port_of_load
        self.port_of_discharge = port_of_discharge
        self.booking_number = booking_number
        self.events = events or []
        self.search_logs = search_logs or []
    
    def add_search_log(self, status: SearchStatus):
        log = SearchLog(timestamp=datetime.now(), status=status)
        self.search_logs.append(log)