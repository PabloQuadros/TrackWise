from typing import List, Optional

from src.enums.ShippingStatus import ShippingStatus
from src.enums.Shipowners import Shipowners

class EventDTO:
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
    
class ContainerDTO:
    def __init__(
        self,
        number: str,
        shipped_from: str,
        shipped_to: str,
        port_of_load: str,
        port_of_discharge: str,
        events: Optional[List[EventDTO]] = None,
        booking_number: Optional[str] = None,
        master_bill_of_lading_number: Optional[str] = None,
        house_bill_of_lading_number: Optional[str] = None,
        _id: Optional[str] = None
    ):
        self._id = _id or None
        self.number = number
        self.shipped_from = shipped_from
        self.shipped_to = shipped_to
        self.port_of_load = port_of_load
        self.port_of_discharge = port_of_discharge
        self.booking_number = booking_number
        self.master_bill_of_lading_number = master_bill_of_lading_number
        self.house_bill_of_lading_number = house_bill_of_lading_number
        self.events = events or []