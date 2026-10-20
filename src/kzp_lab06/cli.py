"""Командний рядок: межа, де помилки перетворюються на повідомлення."""

import argparse
import sys
from datetime import date
from pathlib import Path

from kzp_lab06.analysis import make_summary
from kzp_lab06.errors import DataError
from kzp_lab06.loader import load_records
from kzp_lab06.reporting import format_report, write_report

EXIT_OK = 0
EXIT_DATA_ERROR = 1
EXIT_FILE_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    """Створює парсер аргументів командного рядка."""
    parser = argparse.ArgumentParser(
        prog="kzp-lab06", description="Звіт за бронюваннями готелю з CSV."
    )
    parser.add_argument("input", type=Path, help="вхідний CSV")
    parser.add_argument("output", type=Path, help="файл текстового звіту")
    parser.add_argument(
        "--reference-date",
        type=date.fromisoformat,
        default=None,
        help="дата відбору активних бронювань YYYY-MM-DD (за замовчуванням сьогодні)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Запускає програму та повертає код завершення (0 — успіх)."""
    # Консоль Windows може мати інше кодування, тому UTF-8 задається явно.
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    reference_date = args.reference_date or date.today()
    try:
        records = load_records(args.input)
        text = format_report(make_summary(records, reference_date))
        write_report(args.output, text)
    except DataError as error:
        print(f"Помилка даних: {error}", file=sys.stderr)
        return EXIT_DATA_ERROR
    except OSError as error:
        print(f"Помилка файлу: {error}", file=sys.stderr)
        return EXIT_FILE_ERROR
    print(text, end="")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
