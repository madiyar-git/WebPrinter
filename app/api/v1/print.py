import os
import uuid
import shutil
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status

from app.schemas.print_job import PrintJobResponse
from app.services.printer import send_file_to_printer

router = APIRouter(prefix="/print", tags=["Print"])

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg", ".jpeg", ".doc", ".docx"}


@router.post(
    "",
    response_model=PrintJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Отправка документа на печать"
)
async def create_print_job(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(description="Загружаемый документ")],
    printer_name: Annotated[str | None, Form(description="Имя принтера (если не указан, используется по умолчанию)")] = None,
):
    # Проверка расширения файла
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неподдерживаемый формат файла: {file_ext}. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Генерируем уникальное имя файла для предотвращения перезаписи
    job_id = str(uuid.uuid4())
    safe_filename = f"{job_id}_{file.filename}"
    saved_file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Сохраняем файл на диск asynchronously
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось сохранить загруженный файл: {str(e)}"
        )
    finally:
        await file.close()

    # Добавляем задачу отправки на печать в фоновый поток FastAPI
    background_tasks.add_task(
        send_file_to_printer,
        file_path=saved_file_path,
        printer_name=printer_name
    )

    return PrintJobResponse(
        job_id=job_id,
        filename=file.filename,
        printer_name=printer_name or "Принтер по умолчанию",
        status="pending",
        message="Файл успешно принят и отправлен в очередь печати"
    )