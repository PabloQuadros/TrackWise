from pydantic import BaseModel, Field, StringConstraints, field_validator
from typing import Annotated, Optional
import re

class ContainerCreate(BaseModel):
    number: Annotated[
        str,
        StringConstraints(min_length=11, max_length=11, pattern=r"^[A-Z]{4}\d{7}$")
    ] = Field(
        ..., example="MSCU1234567", description="Número do container com 4 letras e 7 dígitos"
    )

    shipping_company: Annotated[
        str,
        StringConstraints(min_length=1)
    ] = Field(
        ..., example="MSC", description="Nome do armador"
    )

    booking_number: Optional[str] = Field(
        None, example="BOOK123456", description="Número do booking (opcional)"
    )

    @field_validator("number")
    @classmethod
    def validate_container_number_format(cls, value: str) -> str:
        pattern = r"^[A-Z]{4}\d{7}$"
        if not re.match(pattern, value):
            raise ValueError("O número do container deve conter 4 letras seguidas de 7 dígitos (ex: MSCU1234567).")
        return value
