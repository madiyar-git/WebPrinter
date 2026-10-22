import logging
from typing import Any, Dict, List
import win32print

logger = logging.getLogger(__name__)


def get_system_printers() -> List[Dict[str, Any]]:
    """Получает список всех локальных и сетевых принтеров через Win32 API."""
    # PRINTER_ENUM_LOCAL — локальные принтеры
    # PRINTER_ENUM_CONNECTIONS — сетевые принтеры, подключенные к пользователю
    flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS

    default_printer_name = None
    try:
        default_printer_name = win32print.GetDefaultPrinter()
    except Exception as e:
        logger.warning(f"Не удалось определить принтер по умолчанию: {e}")

    try:
        # Level=2 возвращает структуру PRINTER_INFO_2 с деталями о порте, драйвере и статусе
        printers_tuple = win32print.EnumPrinters(flags, None, 2)
    except Exception as e:
        logger.error(f"Ошибка вызова win32print.EnumPrinters: {e}")
        return []

    printers = []
    for printer in printers_tuple:
        printer_name = printer.get("pPrinterName", "")
        printers.append(
            {
                "name": printer_name,
                "driver_name": printer.get("pDriverName"),
                "port_name": printer.get("pPortName"),
                "is_default": printer_name == default_printer_name,
                "status": printer.get("Status", 0),
            }
        )

    return printers