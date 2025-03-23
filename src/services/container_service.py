from typing import Optional
from database.connection import db
from models.container import Container

def save_container(container: Container):
    container_dict = container.dict()  # Converte para dicionário
    db.containers.insert_one(container_dict)
    print("Container salvo com sucesso!")

def get_container_by_number(self, container_number: str) -> Optional[dict]:
    containers_collection = self.db["containers"]
    container = containers_collection.find_one({"ContainerNumber": container_number})
    return container