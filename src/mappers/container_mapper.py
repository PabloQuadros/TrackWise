from src.models.container_create import ContainerCreate
from src.models.container_view import ContainerView, EventView, SearchLogView
from src.domain.container import Container, Event
from datetime import datetime

class ContainerMapper:
    def complete_container_model_with_request_data(self, container: Container, create_model: ContainerCreate) -> Container:
        container.booking_number = create_model.booking_number
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
    
    def from_dict_to_view(self, data: dict) -> ContainerView:
        events = [EventView(**event) for event in data.get("events", [])]
        
        search_logs = [
            SearchLogView(
                timestamp=datetime.fromisoformat(log["timestamp"]),
                status=log["status"]
            )
            for log in data.get("search_logs", [])
            ]   

        return ContainerView(
            _id=str(data.get("_id")),
            bill_of_lading_number=data.get("bill_of_lading_number", ""),
            booking_number=data.get("booking_number", "") or "",
            number=data.get("number", ""),
            shipped_from=data.get("shipped_from", ""),
            shipped_to=data.get("shipped_to", ""),
            port_of_load=data.get("port_of_load", ""),
            port_of_discharge=data.get("port_of_discharge", ""),
            events=events,
            search_logs=search_logs
        )
    
    def from_domain_to_dict(self, container: Container) -> dict:
        return {
            "bill_of_lading_number": container.bill_of_lading_number,
            "booking_number": container.booking_number,
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
                    "status": log.status.value  # salva como string do enum
                }
                for log in container.search_logs
            ]
        }


def get_container_mapper():
    return ContainerMapper()