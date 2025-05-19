from src.models.container_create import ContainerCreate
from src.models.container_view import ContainerView, EventView, SearchLogView
from src.models.container_grid import ContainerGrid
from src.domain.container import Container, Event, SearchLog, SearchStatus
from datetime import datetime
from bson import ObjectId

class ContainerMapper:
    def complete_container_model_with_request_data(self, container: Container, create_model: ContainerCreate) -> Container:
        container.booking_number = create_model.booking_number
        container.master_document_number = create_model.master_document_number
        container.house_document_number = create_model.house_document_number
        return container

    def from_api_response_to_domain_model(self, response_data):
        try:
            bl_data = response_data["Data"]["BillOfLadings"][0]  # Pegando o primeiro BL
            container_data = bl_data["ContainersInfo"][0]  # Pegando o primeiro contêiner

            return Container(
                bill_of_lading_number=bl_data.get("BillOfLadingNumber", ""),
                number=container_data.get("ContainerNumber", ""),
                shipped_from=bl_data.get("GeneralTrackingInfo", {}).get("ShippedFrom", ""),
                shipped_to=bl_data.get("GeneralTrackingInfo", {}).get("ShippedTo", ""),
                port_of_load=bl_data.get("GeneralTrackingInfo", {}).get("PortOfLoad", ""),
                port_of_discharge=bl_data.get("GeneralTrackingInfo", {}).get("PortOfDischarge", ""),
                events=[
                    Event(
                        order=event.get("Order", 0),
                        date=event.get("Date", ""),
                        location=event.get("Location", ""),
                        un_location_code=event.get("UnLocationCode", "") or "",
                        description=event.get("Description", ""),
                        detail=event.get("Detail", [])
                    ) for event in container_data.get("Events", [])
                ]
            )
        except KeyError as e:
            print(f"Erro ao processar a resposta da API: chave ausente {e}")
            return None
    
    def from_domain_to_view(self, container: Container) -> ContainerView:
        events = [
            EventView(
                order=event.order,
                date=event.date,
                location=event.location,
                un_location_code=event.un_location_code,
                description=event.description,
                detail=event.detail
            )
            for event in container.events
        ]

        search_logs = [
            SearchLogView(
                timestamp=log.timestamp,
                status=log.status.value  # Convertendo Enum para string
            )
            for log in container.search_logs
        ]

        return ContainerView(
            _id=str(container._id) if container._id else None,
            bill_of_lading_number=container.bill_of_lading_number,
            booking_number=container.booking_number or "",
            master_document_number=container.master_document_number or "",
            house_document_number=container.house_document_number or "",
            number=container.number,
            shipped_from=container.shipped_from,
            shipped_to=container.shipped_to,
            port_of_load=container.port_of_load,
            port_of_discharge=container.port_of_discharge,
            events=events,
            search_logs=search_logs
        )
        
    def from_domain_to_dict(self, container: Container) -> dict:
        data = {
            "bill_of_lading_number": container.bill_of_lading_number,
            "booking_number": container.booking_number,
            "master_document_number": container.master_document_number,
            "house_document_number": container.house_document_number,
            "number": container.number,
            "shipped_from": container.shipped_from,
            "shipped_to": container.shipped_to,
            "port_of_load": container.port_of_load,
            "port_of_discharge": container.port_of_discharge,
            "events": [
                {
                    "order": event.order,
                    "date": event.date,
                    "location": event.location,
                    "un_location_code": event.un_location_code,
                    "description": event.description,
                    "detail": event.detail
                }
                for event in container.events
            ],
            "search_logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "status": log.status.value
                }
                for log in container.search_logs
            ]
        }

        if container._id is not None:
            data["_id"] = ObjectId(container._id)

        return data
    
    def from_dict_to_domain(self, data: dict) -> Container:
        events = [
            Event(
                order=event.get("order", 0),
                date=event.get("date", ""),
                location=event.get("location", ""),
                un_location_code=event.get("un_location_code", ""),
                description=event.get("description", ""),
                detail=event.get("detail", [])
            )
            for event in data.get("events", [])
        ]

        search_logs = [
            SearchLog(
                timestamp=datetime.fromisoformat(log["timestamp"]),
                status=SearchStatus(log["status"])  # Convertendo de string para Enum
            )
            for log in data.get("search_logs", [])
        ]

        return Container(
            _id=str(data.get("_id")) if data.get("_id") else None,
            number=data.get("number", ""),
            bill_of_lading_number=data.get("bill_of_lading_number", ""),
            shipped_from=data.get("shipped_from", ""),
            shipped_to=data.get("shipped_to", ""),
            port_of_load=data.get("port_of_load", ""),
            port_of_discharge=data.get("port_of_discharge", ""),
            booking_number=data.get("booking_number", ""),
            master_document_number=data.get("master_document_number", ""),
            house_document_number=data.get("house_document_number", ""),
            events=events,
            search_logs=search_logs
        )
    
    def to_container_grid(self, container: dict) -> ContainerGrid:

        # Obter a descrição do evento com maior ordem
        events = container.get("events", [])
        if events:
            latest_event = max(events, key=lambda e: e.get("order", 0))
            description = latest_event.get("description", "")
        else:
            description = ""

        # Obter o último search log com status Sucesso
        search_logs = container.get("search_logs", [])
        successful_logs = [
            log for log in search_logs if log.get("status") == SearchStatus.SUCCESS.value
        ]
        if successful_logs:
            latest_log = max(successful_logs, key=lambda log: log.get("timestamp"))
            last_update = latest_log.get("timestamp")
        else:
            last_update = None

        # Criar e retornar o ContainerGrid
        return ContainerGrid(
            id=str(container.get("_id")),
            number=container.get("number", ""),
            bill_of_lading_number=container.get("bill_of_lading_number", ""),
            booking_number=container.get("booking_number", ""),
            description=description,
            last_update=last_update
        )


def get_container_mapper():
    return ContainerMapper()