"""Читання CSV та перетворення рядків на типізовані записи."""

import csv
from datetime import date
from pathlib import Path

from kzp_lab06.errors import DataError

REQUIRED_COLUMNS = ("room", "guest", "check_in", "check_out", "rate")

Record = dict[str, object]


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


def parse_record(row: dict[str, str], row_number: int) -> Record:
    """Перетворює рядок CSV на запис із числами, датами й нормалізованим текстом."""
    try:
        room = int(row["room"])
    except (TypeError, ValueError) as error:
        raise DataError(f"Рядок {row_number}: поле room має бути цілим") from error
    if room <= 0:
        raise DataError(f"Рядок {row_number}: room має бути додатним")

    guest = (row["guest"] or "").strip()
    if not guest:
        raise DataError(f"Рядок {row_number}: поле guest не може бути порожнім")

    check_in = parse_date(row, "check_in", row_number)
    check_out = parse_date(row, "check_out", row_number)
    if check_out <= check_in:
        raise DataError(f"Рядок {row_number}: check_out має бути пізніше за check_in")

    try:
        rate = float(row["rate"])
    except (TypeError, ValueError) as error:
        raise DataError(f"Рядок {row_number}: поле rate має бути числом") from error
    if rate < 0:
        raise DataError(f"Рядок {row_number}: rate не може бути від'ємним")

    return {
        "room": room,
        "guest": guest,
        "check_in": check_in,
        "check_out": check_out,
        "rate": rate,
        "nights": (check_out - check_in).days,
    }


def load_records(path: Path) -> list[Record]:
    """Завантажує записи з CSV.

    Файл без заголовка або без обов'язкових стовпців — це помилка. Файл лише
    із заголовком є коректним порожнім набором і дає порожній список.
    """
    header, rows = read_rows(path)
    if not header:
        raise DataError("Файл порожній: відсутній рядок заголовка")
    missing = [column for column in REQUIRED_COLUMNS if column not in header]
    if missing:
        raise DataError("Відсутні стовпці: " + ", ".join(missing))
    # Номер рядка рахується від 2, бо рядок 1 — заголовок.
    return [parse_record(row, number) for number, row in enumerate(rows, start=2)]
