from pydantic import BaseModel
from typing import Optional

class ContainerUpdate(BaseModel):
    id: str
    booking_number: Optional[str] = None
    house_bill_of_lading_number: Optional[str] = None
