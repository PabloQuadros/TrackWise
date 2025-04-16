from typing import List, Optional
from pydantic import BaseModel, Field

class EventView(BaseModel):
    order: int
    date: str
    location: str
    un_location_code: str
    description: str
    detail: List[str]

    def to_telegram_chat(self) -> str:
        # Formatação do evento
        details = "\n".join(self.detail)
        return f"📅 **Data**: {self.date}\n📍 **Localização**: {self.location}\n🔢 **Código da Localização**: {self.un_location_code}\n📝 **Descrição**: {self.description}\nℹ️ **Detalhes**: {details} \n"

class ContainerView(BaseModel):
    id: Optional[str] = Field(alias="_id") 
    bill_of_lading_number: str
    booking_number: str
    number: str
    shipped_from: str
    shipped_to: str
    port_of_load: str
    port_of_discharge: str
    events: List[EventView] = []

    def to_telegram_chat(self) -> str:
        # Formatação das informações do contêiner
        container_info = (
            f"📦 **Número do Contêiner**: {self.number}\n"
            f"📄 **Número do Bill of Lading**: {self.bill_of_lading_number}\n"
            f"🔢 **Número de Reserva**: {self.booking_number}\n"
            f"🌍 **De**: {self.shipped_from} ➡️ **Para**: {self.shipped_to}\n"
            f"⚓ **Porto de Embarque**: {self.port_of_load}\n"
            f"⚓ **Porto de Desembarque**: {self.port_of_discharge}\n"
            f"📝 **Eventos**:\n\n"
        )

        # Adiciona os eventos formatados
        event_info = "\n".join([event.to_telegram_chat() for event in self.events])

        # Junta as informações do contêiner com os eventos
        return container_info + event_info