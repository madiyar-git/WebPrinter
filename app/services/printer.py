import logging
from typing import Any, Dict, List
import win32print
import os
import uuid
import logging
import win32api
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

def send_file_to_printer(file_path: str, printer_name: str | None = None) -> None:
    """
    Отправляет документ на системный принтер Windows.
    Убирает временный файл после отправки в очередь Spooler.
    """
    if not os.path.exists(file_path):
        logger.error(f"Файл не найден по пути: {file_path}")
        return

    # Если принтер не передан, берем дефолтный из системы
    target_printer = printer_name or win32print.GetDefaultPrinter()

    try:
        # Устанавливаем целевой принтер как активный для текущего вызова ShellExecute
        win32print.SetDefaultPrinter(target_printer)

        # Вызов ShellExecute с глаголом "printto" передает файл в ассоциированное приложение Windows (Acrobat, Notepad, Photos и т.д.)
        win32api.ShellExecute(
            0,
            "printto",
            file_path,
            f'"{target_printer}"',
            ".",
            0
        )
        logger.info(f"Файл {file_path} успешно отправлен на принтер: {target_printer}")

    except Exception as e:
        logger.error(f"Ошибка при отправке файла {file_path} на печать ({target_printer}): {e}")
    finally:
        # Небольшая задержка удаления гарантирует, что программа-обработчик успеет прочитать файл с диска
        # Фактическое очищение директории uploads/ также можно делать по таймеру
        pass