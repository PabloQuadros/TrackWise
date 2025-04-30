from src.domain.container import Container, Event
from src.models.container_create import ContainerCreate
from src.repositories.container_repository import ContainerRepository, get_container_repository
from src.mappers.container_mapper import ContainerMapper, get_container_mapper
from src.services.msc_service import MscService, get_msc_service
from src.services.search_scheduling_service import SearchSchedulingService, get_search_scheduling_service
from typing import Optional, List
from fastapi import Depends, HTTPException
from src.enums.SearchStatus import SearchStatus


class ContainerService:
    def __init__(self, repository: ContainerRepository, container_mapper: ContainerMapper, msc_service: MscService, search_scheduling_service: SearchSchedulingService):
        self.repository = repository
        self.container_mapper = container_mapper
        self.msc_service = msc_service
        self.search_scheduling_service = search_scheduling_service

    async def register_container(self, container_data: ContainerCreate) -> dict:
        # Verifica se já existe o container no banco
        existing_on_database = await self.repository.get_by_number(container_data.number)
        if existing_on_database:
            raise HTTPException(status_code=400, detail="Container já está registrado!")
        #Verifica se o container existe no site do armador
        existing_on_shipowner = await self.msc_service.validate_container_existence(container_data.number)
        if existing_on_shipowner.get("IsSuccess") is False:
            raise HTTPException(status_code=404, detail="O número do container informado não foi localizado no site do armador")
        #Mapeia da response do armador para a entidade de dominio
        container = self.container_mapper.from_api_response_to_domain_model(existing_on_shipowner)
        #Completa com as informações da requisição
        container.add_search_log(SearchStatus.SUCCESS)
        container = self.container_mapper.complete_container_model_with_request_data(container, container_data)
        await self.repository.save(container)
        await self.search_scheduling_service.add_container_schedule(container.number)
        return {"message": "Container registrado com sucesso!", "data": container_data.dict()}

    async def find_by_container_number(self, container_number: str) -> Optional[dict]:
        container = await self.repository.get_by_number(container_number)
        if container:
            return self.container_mapper.from_domain_to_view(container)
        return None       
    
    async def compare_and_update_container(self, existing: Container, new_data: Container) -> List[str]:
        changes = []

        if existing.bill_of_lading_number != new_data.bill_of_lading_number:
            existing.bill_of_lading_number = new_data.bill_of_lading_number
            changes.append("Bill of Lading Number changed")

        if existing.shipped_from != new_data.shipped_from:
            existing.shipped_from = new_data.shipped_from
            changes.append("Shipped From changed")

        if existing.shipped_to != new_data.shipped_to:
            existing.shipped_to = new_data.shipped_to
            changes.append("Shipped To changed")

        if existing.port_of_load != new_data.port_of_load:
            existing.port_of_load = new_data.port_of_load
            changes.append("Port of Load changed")

        if existing.port_of_discharge != new_data.port_of_discharge:
            existing.port_of_discharge = new_data.port_of_discharge
            changes.append("Port of Discharge changed")

        # Comparação mais detalhada dos eventos
        old_events = {self._event_key(e): e for e in existing.events}
        new_events = {self._event_key(e): e for e in new_data.events}

        added_keys = new_events.keys() - old_events.keys()
        removed_keys = old_events.keys() - new_events.keys()
        common_keys = old_events.keys() & new_events.keys()

        for key in added_keys:
            changes.append(f"Novo evento adicionado: {new_events[key].description} em {new_events[key].location}")

        for key in removed_keys:
            changes.append(f"Evento removido: {old_events[key].description} em {old_events[key].location}")

        for key in common_keys:
            old_event = old_events[key]
            new_event = new_events[key]
            if old_event.__dict__ != new_event.__dict__:
                changes.append(f"Evento atualizado: {old_event.description} → {new_event.description} em {old_event.location}")

        if changes:
            existing.events = new_data.events
        
        await self.repository.update(existing)

        return changes

    def _event_key(self, event: Event) -> str:
        # Chave única do evento — você pode mudar isso conforme sua lógica
        return f"{event.order}-{event.date}-{event.location}"



def get_container_service(
    repository: ContainerRepository = Depends(get_container_repository), 
    container_mapper: ContainerMapper = Depends(get_container_mapper),
    msc_service: MscService = Depends(get_msc_service),
    search_scheduling_service: SearchSchedulingService = Depends(get_search_scheduling_service)
) -> ContainerService:
    return ContainerService(repository, container_mapper, msc_service, search_scheduling_service)