from typing import Optional
from src.database.connection import db
from src.domain.container import Container

class ContainerRepository:
    def __init__(self):
        self.collection = db["containers"]

    def save(self, container: Container) -> None:
        container_dict = container.model_dump()
        self.collection.insert_one(container_dict)
        print("Container salvo com sucesso!")

    def get_by_number(self, container_number: str) -> Optional[dict]:
        return self.collection.find_one({"number": container_number})
    
def get_container_repository():
    return ContainerRepository()
