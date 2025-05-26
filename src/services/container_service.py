from src.domain.container import Container, Event
from src.models.container_create import ContainerCreate
from src.repositories.container_repository import ContainerRepository, get_container_repository
from src.mappers.container_mapper import ContainerMapper, get_container_mapper
from src.services.msc_service import MscService, get_msc_service
from src.services.search_scheduling_service import SearchSchedulingService, get_search_scheduling_service
from typing import Optional, List
from fastapi import Depends, HTTPException
from src.enums.SearchStatus import SearchStatus
from src.enums.ShippingStatus import ShippingStatus
from src.models.container_grid import ContainerGrid
from src.models.container_dto import ContainerDTO

class ContainerService:
    def __init__(self, repository: ContainerRepository, container_mapper: ContainerMapper, msc_service: MscService, search_scheduling_service: SearchSchedulingService):
        self.repository = repository
        self.container_mapper = container_mapper
        self.msc_service = msc_service
        self.search_scheduling_service = search_scheduling_service

    async def register_container(self, container_data: ContainerCreate) -> dict:
        # Verifica se já existe o container no banco em acompanhamento
        existing_containers = await self.repository.get_all_by_number(container_data.number)
        if any(
            c.shipowner.value == container_data.shipowner.value and c.shipping_status.value == ShippingStatus.PROCESSING.value
            for c in existing_containers
        ):
            raise HTTPException(status_code=400, detail="Container já está registrado!")
        #Verifica se o container existe no site do armador
        shipowner_response = await self.msc_service.validate_container_existence(container_data.number)
        if shipowner_response.get("IsSuccess") is False:
            raise HTTPException(status_code=404, detail="O número do container informado não foi localizado no site do armador")
        #Mapeia da response do armador para a entidade de dominio
        containerDto = self.container_mapper.from_api_response_to_dto_model(shipowner_response)
        #Verificar se já existe o container no banco mas finalizado.
        if any(
            c.shipowner.value == container_data.shipowner.value and c.shipping_status.value == ShippingStatus.FINISHED.value and c.master_bill_of_lading_number == containerDto.master_bill_of_lading_number
            for c in existing_containers
        ):
            raise HTTPException(status_code=400, detail="Container já está registrado!")
        container = Container.build(
            number=containerDto.number,
            shipowner=container_data.shipowner,
            shipped_from=containerDto.shipped_from,
            shipped_to=containerDto.shipped_to,
            port_of_load=containerDto.port_of_load,
            port_of_discharge=containerDto.port_of_discharge,
            events_dto=containerDto.events,
            booking_number=container_data.booking_number,
            master_bill_of_lading_number=containerDto.master_bill_of_lading_number,
            house_bill_of_lading_number=container_data.house_document_number
        )

        container.add_search_log(SearchStatus.SUCCESS)

        
        await self.repository.save(container)
        if container.shipping_status == ShippingStatus.PROCESSING:
            await self.search_scheduling_service.add_container_schedule(container.number)
        return {"message": "Container registrado com sucesso!", "data": container_data.dict()}

    async def find_by_container_number(self, container_number: str) -> Optional[dict]:
        container = await self.repository.get_by_number(container_number)
        if container:
            return self.container_mapper.from_domain_to_view(container)
        return None       
    
    async def compare_and_update_container(self, existing: Container, new_data: ContainerDTO) -> Container:
        changes = []

        if existing.master_bill_of_lading_number != new_data.master_bill_of_lading_number:
            existing.master_bill_of_lading_number = new_data.master_bill_of_lading_number
            changes.append("Número do Master Bill Of Lading alterado")

        if existing.shipped_from != new_data.shipped_from:
            existing.shipped_from = new_data.shipped_from
            changes.append("Origem do Envio alterada")

        if existing.shipped_to != new_data.shipped_to:
            existing.shipped_to = new_data.shipped_to
            changes.append("Destino do Envio alterado")

        if existing.port_of_load != new_data.port_of_load:
            existing.port_of_load = new_data.port_of_load
            changes.append("Porto de Embarque alterado")

        if existing.port_of_discharge != new_data.port_of_discharge:
            existing.port_of_discharge = new_data.port_of_discharge
            changes.append("Porto de Desembarque alterado")

        # Comparação mais detalhada dos eventos
        old_events = {self.event_key(e): e for e in existing.events}
        new_events = {self.event_key(e): e for e in new_data.events}

        added_keys = new_events.keys() - old_events.keys()
        removed_keys = old_events.keys() - new_events.keys()
        common_keys = old_events.keys() & new_events.keys()

        for key in added_keys:
            changes.append(f"Novo evento adicionado: {new_events[key].description} em {new_events[key].location}")
            existing.add_event(new_events[key])

        for key in removed_keys:
            changes.append(f"Evento removido: {old_events[key].description} em {old_events[key].location}")
            existing.remove_event_by_order(old_events[key])

        for key in common_keys:
            old_event = old_events[key]
            new_event = new_events[key]
            if old_event.__dict__ != new_event.__dict__:
                changes.append(f"Evento atualizado: {old_event.date} → {new_event.date} | {old_event.location} → {new_event.location} | "
                               f"{old_event.un_location_code} → {new_event.un_location_code} | {old_event.description} → {new_event.description} | "
                               f"{old_event.detail} → {new_event.detail}")
                existing.update_event(new_event.date, new_event.location, new_event.un_location_code, new_event.description, new_event.detail)

        existing.add_search_log(SearchStatus.SUCCESS)
        existing.set_shipping_status()
        await self.repository.update(existing)
        if changes:
                for change in changes:
                    print(change)
        else:
            print("Nenhuma mudança detectada nas informações do contêiner.")

        return existing

    def event_key(self, event: Event) -> str:
        # Chave única do evento
        return f"{event.order}"
    
    async def get_all_for_grid(self) -> List[ContainerGrid]:
        documents = await self.repository.find_all_for_grid()
        result = [self.container_mapper.to_container_grid(doc) for doc in documents]
        return result
    
    async def get_container_by_id (self, id: str) -> Optional[dict]:
        container = await self.repository.get_by_id(id)
        if container:
            return self.container_mapper.from_domain_to_view(container)
        return None  


def get_container_service(
    repository: ContainerRepository = Depends(get_container_repository), 
    container_mapper: ContainerMapper = Depends(get_container_mapper),
    msc_service: MscService = Depends(get_msc_service),
    search_scheduling_service: SearchSchedulingService = Depends(get_search_scheduling_service)
) -> ContainerService:
    return ContainerService(repository, container_mapper, msc_service, search_scheduling_service)