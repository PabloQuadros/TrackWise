from typing import List, Optional
from pydantic import BaseModel


class Event(BaseModel):
    order: int
    date: str
    location: str
    un_location_code: str
    description: str
    detail: List[str]


class Container(BaseModel):
    bill_of_lading_number: str
    booking_number: Optional[str] = None
    number: str
    shipped_from: str
    shipped_to: str
    port_of_load: str
    port_of_discharge: str
    events: List[Event] = []
    