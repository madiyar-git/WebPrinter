from pydantic import BaseModel, Field


class PrintJobResponse(BaseModel):
    job_id: str = Field(..., description="Уникальный идентификатор задачи")
    filename: str = Field(..., description="Имя оригинального файла")
    printer_name: str = Field(..., description="Целевой принтер")
    status: str = Field(..., description="Текущий статус (pending / processing / completed / error)")
    message: str = Field(..., description="Детали выполнения")