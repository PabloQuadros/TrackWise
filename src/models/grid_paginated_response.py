from pydantic import BaseModel
from typing import List
from src.models.container_grid import ContainerGrid

class GridPaginatedResponse(BaseModel):
    items: List[ContainerGrid]
    total: int
    page: int
    page_size: int
