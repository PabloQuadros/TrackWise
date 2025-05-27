from typing import List, Optional
from src.enums.SearchStatus import SearchStatus
from src.enums.ShippingStatus import ShippingStatus
from src.enums.Shipowners import Shipowners
from src.enums.EventStatus import EventStatus
from datetime import datetime

class SearchLog:
    def __init__(self, timestamp: datetime, status: SearchStatus):
        self.timestamp = timestamp
        self.status = status

class Event:
    def __init__(
        self,
        order: int,
        location: str,
        un_location_code: str,
        description: str,
        detail: Optional[List[str]] = None,
        status: Optional[EventStatus] = None,
        estimated_date: Optional[str] = None,
        effective_date: Optional[str] = None,
    ):
        self.order = order
        self.estimated_date = estimated_date
        self.effective_date = effective_date
        self.location = location
        self.un_location_code = un_location_code
        self.description = description
        self.detail = detail
        self.status = status

    @classmethod
    def build(       
        cls,
        order: int,
        location: str,
        un_location_code: str,
        description: str,
        detail: List[str],
        estimated_date: Optional[str] = None,
        effective_date: Optional[str] = None,
    ):
        event = cls(
            order = order,
            location = location,
            un_location_code = un_location_code,
            description = description,
            detail = detail,
            estimated_date = estimated_date,
            effective_date = effective_date,    
        )
        event.set_event_status()
        return event
    
    def set_event_status(self):
        if self.effective_date is not None:
            self.status = EventStatus.EFFECTIVE
        else:
            self.status = EventStatus.ESTIMATED

    
class Container:
    def __init__(
        self,
        number: str,
        shipowner: Shipowners,
        shipped_from: str,
        shipped_to: str,
        port_of_load: str,
        port_of_discharge: str,
        shipping_status: Optional[ShippingStatus] = None,
        events: Optional[List[Event]] = None,
        booking_number: Optional[str] = None,
        master_bill_of_lading_number: Optional[str] = None,
        house_bill_of_lading_number: Optional[str] = None,
        search_logs: Optional[List[SearchLog]] = None,
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
        self.search_logs = search_logs or []
        self.shipping_status= shipping_status
        self.shipowner = shipowner

    @classmethod
    def build(
        cls,
        number: str,
        shipowner: Shipowners,
        shipped_from: str,
        shipped_to: str,
        port_of_load: str,
        port_of_discharge: str,
        events_dto: Optional[List[Event]] = None,
        booking_number: Optional[str] = None,
        master_bill_of_lading_number: Optional[str] = None,
        house_bill_of_lading_number: Optional[str] = None,
    ):
        container = cls(
            number = number,
            shipped_from = shipped_from,
            shipped_to = shipped_to,
            port_of_load = port_of_load,
            port_of_discharge = port_of_discharge,
            booking_number = booking_number,
            master_bill_of_lading_number = master_bill_of_lading_number,
            house_bill_of_lading_number = house_bill_of_lading_number,
            events=[
                    Event.build(
                        order=event.order,
                        estimated_date=event.estimated_date,
                        effective_date=event.effective_date,
                        location=event.location,
                        un_location_code=event.un_location_code or "",
                        description=event.description or "",
                        detail=event.detail or []
                    ) for event in events_dto
                ] or [],
            search_logs = [],
            shipping_status = None,
            shipowner = shipowner
        )
        container.set_shipping_status()
        return container
        
    
    def add_search_log(self, status: SearchStatus):
        log = SearchLog(timestamp=datetime.now(), status=status)
        self.search_logs.append(log)
    
    def set_shipping_status(self):
        if self.events:
            last_event = max(self.events, key=lambda e: e.order)

        is_empty_received = (
            last_event.description == "Empty received at CY" and
            " ".join(last_event.detail) == "EMPTY" and last_event.status is EventStatus.EFFECTIVE
        )

        if is_empty_received:
            self.shipping_status = ShippingStatus.FINISHED
        else:
            self.shipping_status = ShippingStatus.PROCESSING
    
    def add_event(self, event: Event):
        if any(e.order == event.order for e in self.events):
            return

        self.events.append(
            Event.build(
                order=event.order,
                estimated_date=event.estimated_date,
                effective_date=event.effective_date,
                location=event.location,
                un_location_code=event.un_location_code or "",
                description=event.description or "",
                detail=event.detail or []
            )
        )
    
    def remove_event_by_order(self, order: int):
        self.events = [e for e in self.events if e.order != order]
                
    def update_event(
        self, 
        order: int, 
        location: str,
        un_location_code: str,
        description: str,
        detail: List[str],
        estimated_date: Optional[str] = None,
        effective_date: Optional[str] = None, ):
        event = next((e for e in self.events if e.order == order), None)
        if event:
            if event.estimated_date != None:
                event.date = estimated_date
            if event.effective_date != None:
                event.effective_date = effective_date
            if event.location != location:
                event.location = location
            if event.un_location_code != un_location_code:
                event.un_location_code = un_location_code
            if event.description != description:
                event.description = description
            if event.detail != detail:
                event.detail = detail
            event.set_event_status()
