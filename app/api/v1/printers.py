from typing import List
from fastapi import APIRouter, HTTPException, status

from app.schemas.printer import PrinterResponse
from app.services.printer import get_system_printers

router = APIRouter(prefix="/printers", tags=["Printers"])


@router.get("", response_model=List[PrinterResponse], summary="Список доступных принтеров")
async def list_printers():
    try:
        return get_system_printers()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка взаимодействия с подсистемой печати: {str(e)}",
        )