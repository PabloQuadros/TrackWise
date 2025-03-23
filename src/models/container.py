from dataclasses import dataclass, field
from typing import List

@dataclass
class Event:
    order: int
    date: str
    location: str
    un_location_code: str
    description: str
    detail: List[str]

@dataclass
class Container:
    bill_of_lading_number: str
    number: str
    shipped_from: str
    shipped_to: str
    port_of_load: str
    port_of_discharge: str
    events: List[Event] = field(default_factory=list)

    @staticmethod
    def from_api_response(response_data):
        """
        Converte os dados da resposta da API em um objeto Container.
        """
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
                events=[
                    Event(
                        order=event["Order"],
                        date=event["Date"],
                        location=event["Location"],
                        un_location_code=event["UnLocationCode"],
                        description=event["Description"],
                        detail=event.get("Detail", [])
                    ) for event in container_data["Events"]
                ]
            )
        except KeyError as e:
            print(f"Erro ao processar a resposta da API: chave ausente {e}")
            return None
