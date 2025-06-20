from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from src.enums.SearchStatus import SearchStatus

class SearchLogView(BaseModel):
    timestamp: datetime
    status: SearchStatus

class EventView(BaseModel):
    order: int
    location: str
    un_location_code: str
    description: str
    status: str
    detail: Optional[List[str]] = None
    estimated_date: Optional[str] = None,
    effective_date: Optional[str] = None,

    def to_telegram_chat(self) -> str:
        # Formatação do evento
        details = "\n".join(self.detail)
        return f"📅 **Data Estimada**: {self.estimated_date or '-'}\n📅 **Data Efetiva**: {self.effective_date or '-'}\n📍 **Localização**: {self.location}\n🔢 **Código da Localização**: {self.un_location_code}\n📝 **Descrição**: {self.description}\nℹ️ **Detalhes**: {details or '-'} \n🕐 **Status**: {self.status or '-'} \n"

class ContainerView(BaseModel):
    id: Optional[str] = Field(alias="_id") 
    booking_number: str
    master_bill_of_lading_number: str
    house_bill_of_lading_number: str
    number: str
    shipped_from: str
    shipped_to: str
    port_of_load: str
    port_of_discharge: str
    events: List[EventView] = []
    search_logs: List[SearchLogView] = []
    shipping_status: Optional[str] = None
    shipowner: Optional[str] = None

    def to_telegram_chat(self) -> str:
        # Formatação das informações do contêiner
        container_info = (
            f"📦 **Número do Contêiner**: {self.number}\n"
            f"🚢 **Armador**: {self.shipowner}\n"
            f"🔢 **Número de Reserva**: {self.booking_number}\n"
            f"📄 **Número do Master Bill of Lading**: {self.master_bill_of_lading_number}\n"
            f"📄 **Número do House Bill of Lading**: {self.house_bill_of_lading_number}\n"
            f"🌍 **De**: {self.shipped_from} ➡️ **Para**: {self.shipped_to}\n"
            f"⚓ **Porto de Embarque**: {self.port_of_load}\n"
            f"⚓ **Porto de Desembarque**: {self.port_of_discharge}\n"
            f"🕐 **Status da Viagem**: {self.shipping_status}\n"
            f"📝 **Eventos**:\n\n"
        )

        # Adiciona os eventos formatados
        event_info = "\n".join([event.to_telegram_chat() for event in self.events])
        
         # Logs de busca formatados (opcional)
        if self.search_logs:
            logs_info = "\n📊 **Histórico de Buscas**:\n"
            for log in self.search_logs:
                logs_info += f"🕒 {log.timestamp.strftime('%d/%m/%Y %H:%M:%S')} - {log.status.value}\n"
        else:
            logs_info = "\n📊 **Histórico de Buscas**: Nenhum registro\n"

        # Junta as informações do contêiner com os eventos
        return container_info + event_info + logs_info