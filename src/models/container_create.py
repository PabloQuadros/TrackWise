from pydantic import BaseModel, Field, StringConstraints, field_validator
from typing import Annotated, Optional
import re
from src.enums.Shipowners import Shipowners

class ContainerCreate(BaseModel):
    number: Annotated[
        str,
        StringConstraints(min_length=11, max_length=11, pattern=r"^[A-Z]{4}\d{7}$")
    ] = Field(
        ..., example="MSCU1234567", description="Número do container com 4 letras e 7 dígitos"
    )

    shipowner: Shipowners = Field(
        ..., example="MSC", description="Nome do armador"
    )

    booking_number: Optional[str] = Field(
        None, example="BOOK123456", description="Número do booking (opcional)"
    )
 
    house_document_number: Optional[str] = Field(
        None, example="FF12345678", description="Número do House Bill of Lading (opcional)"
    )

    @field_validator("number")
    @classmethod
    def validate_container_number_format(cls, value: str) -> str:
        pattern = r"^[A-Z]{4}\d{7}$"
        if not re.match(pattern, value):
            raise ValueError("O número do container deve conter 4 letras seguidas de 7 dígitos (ex: MSCU1234567).")
        return value
