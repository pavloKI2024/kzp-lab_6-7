"""Тести завантаження CSV в об'єкти."""

from datetime import date
from pathlib import Path

import pytest

from kzp_lab07.errors import DataError
from kzp_lab07.loader import load_bookings
from kzp_lab07.models import PremiumBooking, StandardBooking

HEADER = "room,guest,check_in,check_out,rate\n"
ROOT = Path(__file__).resolve().parent.parent


def write_csv(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "input.csv"
    path.write_text(text, encoding="utf-8", newline="")
    return path


def test_valid_csv_gives_objects_of_both_subtypes(tmp_path: Path) -> None:
    text = (
        HEADER + "101,А,2026-10-01,2026-10-04,1200\n102,Б,2026-10-01,2026-10-04,2500\n"
    )

    bookings = load_bookings(write_csv(tmp_path, text))

    assert [type(b) for b in bookings] == [StandardBooking, PremiumBooking]
    assert bookings[0].check_in == date(2026, 10, 1)


def test_real_data_file_is_loaded() -> None:
    bookings = load_bookings(ROOT / "data" / "bookings.csv")

    assert len(bookings) == 7
    assert bookings[4] == bookings[5]


def test_header_only_file_gives_empty_list(tmp_path: Path) -> None:
    assert load_bookings(write_csv(tmp_path, HEADER)) == []


def test_completely_empty_file_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(DataError, match="заголовка"):
        load_bookings(write_csv(tmp_path, ""))


def test_missing_column_is_reported(tmp_path: Path) -> None:
    with pytest.raises(DataError, match="Відсутні стовпці: rate"):
        load_bookings(write_csv(tmp_path, "room,guest,check_in,check_out\n"))


def test_comma_and_quotes_in_guest_are_read(tmp_path: Path) -> None:
    text = HEADER + '1,"Коваль, ""Лі"" Олена",2026-10-02,2026-10-09,100\n'

    assert load_bookings(write_csv(tmp_path, text))[0].guest == 'Коваль, "Лі" Олена'


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ("abc,А,2026-10-01,2026-10-04,1", "Рядок 2: поле room має бути цілим"),
        ("1,А,2026-10-01,2026-10-04,abc", "Рядок 2: поле rate має бути числом"),
        ("1,А,не-дата,2026-10-04,1", "Рядок 2: поле check_in має бути датою"),
        ("0,А,2026-10-01,2026-10-04,1", "Рядок 2: room має бути додатним"),
        ("1,  ,2026-10-01,2026-10-04,1", "Рядок 2: guest не може бути порожнім"),
        ("1,А,2026-10-04,2026-10-01,1", "Рядок 2: check_out має бути пізніше"),
        ("1,А,2026-10-01,2026-10-04,-5", "Рядок 2: rate не може бути від'ємним"),
        ("1,А,2026-10-01", "Рядок 2: поле check_out має бути датою"),
    ],
)
def test_bad_rows_report_row_number(tmp_path: Path, row: str, message: str) -> None:
    with pytest.raises(DataError, match=message):
        load_bookings(write_csv(tmp_path, HEADER + row + "\n"))


def test_model_error_keeps_value_error_as_cause(tmp_path: Path) -> None:
    text = HEADER + "0,А,2026-10-01,2026-10-04,1\n"

    with pytest.raises(DataError) as info:
        load_bookings(write_csv(tmp_path, text))

    assert isinstance(info.value.__cause__, ValueError)
