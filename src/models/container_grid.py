from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from src.enums.ShippingStatus import ShippingStatus
from src.enums.Shipowners import Shipowners

class ContainerGrid(BaseModel):
    id: Optional[str]
    number: str
    shipowner: str
    master_bill_of_lading_number: str
    booking_number: str
    description: str
    last_update: datetime
    shipping_status: str
