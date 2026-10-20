"""Командний рядок: межа, де помилки перетворюються на повідомлення."""

import argparse
import sys
from datetime import date
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from kzp_lab07.analysis import make_summary, total_revenue
from kzp_lab07.errors import DataError
from kzp_lab07.loader import load_bookings
from kzp_lab07.reporting import format_report, write_report

EXIT_OK = 0
EXIT_DATA_ERROR = 1
EXIT_FILE_ERROR = 2


def get_version() -> str:
    """Повертає версію пакета з його метаданих (джерело — pyproject.toml)."""
    try:
        return version("kzp-lab06")
    except PackageNotFoundError:
        return "unknown"


def build_parser() -> argparse.ArgumentParser:
    """Створює парсер аргументів командного рядка."""
    parser = argparse.ArgumentParser(
        prog="kzp-lab07", description="Звіт за бронюваннями готелю з CSV."
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )
    parser.add_argument("input", type=Path, help="вхідний CSV")
    parser.add_argument("output", type=Path, help="файл текстового звіту")
    parser.add_argument(
        "--reference-date",
        type=date.fromisoformat,
        default=None,
        help="дата відбору активних бронювань YYYY-MM-DD (за замовчуванням сьогодні)",
    )
    parser.add_argument(
        "--with-revenue",
        action="store_true",
        help="додати до звіту виторг за total_price() підтипів",
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
        bookings = load_bookings(args.input)
        revenue = total_revenue(bookings) if args.with_revenue else None
        text = format_report(make_summary(bookings, reference_date), revenue)
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
