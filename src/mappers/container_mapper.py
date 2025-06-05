from src.models.container_create import ContainerCreate
from src.models.container_view import ContainerView, EventView, SearchLogView
from src.models.container_grid import ContainerGrid
from src.domain.container import Container, Event, SearchLog, SearchStatus
from src.models.container_dto import ContainerDTO, EventDTO
from datetime import datetime
from bson import ObjectId
from src.enums.ShippingStatus import ShippingStatus
from src.enums.Shipowners import Shipowners
from src.enums.EventStatus import EventStatus

class ContainerMapper:
    # def complete_container_model_with_request_data(self, container: Container, create_model: ContainerCreate) -> Container:
    #     container.booking_number = create_model.booking_number
    #     container.house_bill_of_lading_number = create_model.house_document_number
    #     container.shipowner = create_model.shipowner
    #     return container

    def from_api_response_to_dto_model(self, response_data):
        try:
            bl_data = response_data["Data"]["BillOfLadings"][0]  # Pegando o primeiro BL
            container_data = bl_data["ContainersInfo"][0]  # Pegando o primeiro contêiner

            return ContainerDTO(
                number=container_data.get("ContainerNumber", ""),
                master_bill_of_lading_number=bl_data.get("BillOfLadingNumber", ""),
                shipped_from=bl_data.get("GeneralTrackingInfo", {}).get("ShippedFrom", ""),
                shipped_to=bl_data.get("GeneralTrackingInfo", {}).get("ShippedTo", ""),
                port_of_load=bl_data.get("GeneralTrackingInfo", {}).get("PortOfLoad", ""),
                port_of_discharge=bl_data.get("GeneralTrackingInfo", {}).get("PortOfDischarge", ""),
                events=[
                    EventDTO(
                        order=event.get("Order", 0),
                        location=event.get("Location", ""),
                        un_location_code=event.get("UnLocationCode", "") or "",
                        description=event.get("Description", ""),
                        detail = (event.get("Detail") or [None]) if (event.get("Detail") or [None])[0] is not None else None,
                        estimated_date=event.get("Date", "") if datetime.strptime(event.get("Date", ""), "%d/%m/%Y") > datetime.now() or "Estimated" in event.get("Description", "") else None,
                        effective_date=event.get("Date", "") if datetime.strptime(event.get("Date", ""), "%d/%m/%Y") <= datetime.now() and "Estimated" not in event.get("Description", "") else None
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
                estimated_date=event.estimated_date,
                effective_date=event.effective_date,
                location=event.location,
                un_location_code=event.un_location_code,
                description=event.description,
                detail=event.detail,
                status=event.status.value
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
            booking_number=container.booking_number or "",
            master_bill_of_lading_number=container.master_bill_of_lading_number or "",
            house_bill_of_lading_number=container.house_bill_of_lading_number or "",
            number=container.number,
            shipped_from=container.shipped_from,
            shipped_to=container.shipped_to,
            port_of_load=container.port_of_load,
            port_of_discharge=container.port_of_discharge,
            events=events,
            search_logs=search_logs,
            shipping_status=container.shipping_status.value,
            shipowner=container.shipowner.value
        )
        
    def from_domain_to_dict(self, container: Container) -> dict:
        data = {
            "booking_number": container.booking_number,
            "master_bill_of_lading_number": container.master_bill_of_lading_number,
            "house_bill_of_lading_number": container.house_bill_of_lading_number,
            "number": container.number,
            "shipped_from": container.shipped_from,
            "shipped_to": container.shipped_to,
            "port_of_load": container.port_of_load,
            "port_of_discharge": container.port_of_discharge,
            "shipping_status": container.shipping_status.value,
            "shipowner": container.shipowner.value,
            "events": [
                {
                    "order": event.order,
                    "estimated_date": event.estimated_date,
                    "effective_date": event.effective_date,
                    "location": event.location,
                    "un_location_code": event.un_location_code,
                    "description": event.description,
                    "detail": event.detail,
                    "status": event.status.value
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
                estimated_date=event.get("estimated_date", None),
                effective_date=event.get("effective_date", None),
                location=event.get("location", ""),
                un_location_code=event.get("un_location_code", ""),
                description=event.get("description", ""),
                detail=event.get("detail", []),
                status=EventStatus(event.get("status")),
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
            shipped_from=data.get("shipped_from", ""),
            shipped_to=data.get("shipped_to", ""),
            port_of_load=data.get("port_of_load", ""),
            port_of_discharge=data.get("port_of_discharge", ""),
            booking_number=data.get("booking_number", ""),
            master_bill_of_lading_number=data.get("master_bill_of_lading_number", ""),
            house_bill_of_lading_number=data.get("house_bill_of_lading_number", ""),
            shipping_status=ShippingStatus(data.get("shipping_status")),
            shipowner=Shipowners(data.get("shipowner")),
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
            master_bill_of_lading_number=container.get("master_bill_of_lading_number", ""),
            shipowner=container.get("shipowner", ""),
            booking_number=container.get("booking_number", ""),
            shipping_status=container.get("shipping_status", ""),
            description=description,
            last_update=last_update
        )


def get_container_mapper():
    return ContainerMapper()