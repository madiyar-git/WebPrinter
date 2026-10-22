from pydantic import BaseModel, Field


class PrinterResponse(BaseModel):
    name: str = Field(..., description="Системное имя принтера")
    driver_name: str | None = Field(None, description="Драйвер устройства")
    port_name: str | None = Field(None, description="Порт (USB, LPT, IP и т.д.)")
    is_default: bool = Field(False, description="Флаг принтера по умолчанию")
    status: int = Field(0, description="Код статуса Windows Spooler")