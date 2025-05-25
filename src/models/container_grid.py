from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from src.enums.SearchStatus import SearchStatus

class ContainerGrid(BaseModel):
    id: Optional[str]
    number: str
    master_bill_of_lading_number: str
    house_bill_of_lading_number: str
    booking_number: str
    description: str
    last_update: datetime