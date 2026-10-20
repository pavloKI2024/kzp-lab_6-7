"""Читання CSV і перетворення рядків на об'єкти бронювань."""

import csv
from datetime import date
from pathlib import Path

from kzp_lab07.errors import DataError
from kzp_lab07.models import Booking, make_booking

REQUIRED_COLUMNS = ("room", "guest", "check_in", "check_out", "rate")


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Читає CSV-файл і повертає заголовок та рядки як словники."""
    # newline="" передає керування роздільниками рядків модулю csv.
    with path.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        rows = list(reader)
        header = list(reader.fieldnames or [])
    return header, rows


def parse_date(row: dict[str, str], field: str, row_number: int) -> date:
    """Перетворює поле на дату формату YYYY-MM-DD."""
    try:
        return date.fromisoformat(row[field].strip())
    except (AttributeError, ValueError) as error:
        raise DataError(
            f"Рядок {row_number}: поле {field} має бути датою YYYY-MM-DD"
        ) from error


def build_booking(row: dict[str, str], row_number: int) -> Booking:
    """Перетворює рядок CSV на бронювання відповідного підтипу."""
    try:
        room = int(row["room"])
    except (TypeError, ValueError) as error:
        raise DataError(f"Рядок {row_number}: поле room має бути цілим") from error
    check_in = parse_date(row, "check_in", row_number)
    check_out = parse_date(row, "check_out", row_number)
    try:
        rate = float(row["rate"])
    except (TypeError, ValueError) as error:
        raise DataError(f"Рядок {row_number}: поле rate має бути числом") from error
    try:
        return make_booking(room, row["guest"] or "", check_in, check_out, rate)
    except ValueError as error:
        # Інваріанти перевіряє сама модель; тут додається контекст рядка.
        raise DataError(f"Рядок {row_number}: {error}") from error


def load_bookings(path: Path) -> list[Booking]:
    """Завантажує бронювання з CSV.

    Файл без заголовка або без обов'язкових стовпців — помилка. Файл лише
    із заголовком є коректним порожнім набором.
    """
    header, rows = read_rows(path)
    if not header:
        raise DataError("Файл порожній: відсутній рядок заголовка")
    missing = [column for column in REQUIRED_COLUMNS if column not in header]
    if missing:
        raise DataError("Відсутні стовпці: " + ", ".join(missing))
    # Номер рядка рахується від 2, бо рядок 1 — заголовок.
    return [build_booking(row, number) for number, row in enumerate(rows, start=2)]
