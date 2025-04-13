from typing import List, Optional
from pydantic import BaseModel, Field

class EventView(BaseModel):
    order: int
    date: str
    location: str
    un_location_code: str
    description: str
    detail: List[str]

class ContainerView(BaseModel):
    id: Optional[str] = Field(alias="_id") 
    bill_of_lading_number: str
    booking_number: str
    number: str
    shipped_from: str
    shipped_to: str
    port_of_load: str
    port_of_discharge: str
    events: List[EventView] = []
