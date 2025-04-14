from src.models.container_create import ContainerCreate
from src.models.container_view import ContainerView, EventView
from src.domain.container import Container, Event

class ContainerMapper:
    def complete_container_model_with_request_data(self, container: Container, create_model: ContainerCreate) -> Container:
        container.booking_number = create_model.booking_number
        return container

    def from_api_response_to_domain_model(self, response_data):
        try:
            bl_data = response_data["Data"]["BillOfLadings"][0]  # Pegando o primeiro BL
            container_data = bl_data["ContainersInfo"][0]  # Pegando o primeiro contêiner

            return Container(
                bill_of_lading_number=bl_data["BillOfLadingNumber"],
                number=container_data["ContainerNumber"],
                shipped_from=bl_data["GeneralTrackingInfo"]["ShippedFrom"],
                shipped_to=bl_data["GeneralTrackingInfo"]["ShippedTo"],
                port_of_load=bl_data["GeneralTrackingInfo"]["PortOfLoad"],
                port_of_discharge=bl_data["GeneralTrackingInfo"]["PortOfDischarge"],
                events=[  # Criando a lista de eventos com base nos dados
                    Event(
                        order=event["Order"],
                        date=event["Date"],
                        location=event["Location"],
                        un_location_code=event["UnLocationCode"],
                        description=event["Description"],
                        detail=event.get("Detail", [])  # Garantindo que o campo 'Detail' não seja nulo
                    ) for event in container_data["Events"]
                ]
            )
        except KeyError as e:
            print(f"Erro ao processar a resposta da API: chave ausente {e}")
            return None
    
    def from_dict_to_view(self, data: dict) -> ContainerView:
        events = [EventView(**event) for event in data.get("events", [])]
        
        return ContainerView(
            _id=str(data.get("_id")),
            bill_of_lading_number=data.get("bill_of_lading_number", ""),
            booking_number=data.get("booking_number", ""),
            number=data.get("number", ""),
            shipped_from=data.get("shipped_from", ""),
            shipped_to=data.get("shipped_to", ""),
            port_of_load=data.get("port_of_load", ""),
            port_of_discharge=data.get("port_of_discharge", ""),
            events=events
        )


def get_container_mapper():
    return ContainerMapper()