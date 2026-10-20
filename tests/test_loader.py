"""Тести завантаження й перетворення CSV."""

from datetime import date
from pathlib import Path

import pytest

from kzp_lab06.errors import DataError
from kzp_lab06.loader import load_records

HEADER = "room,guest,check_in,check_out,rate\n"


def write_csv(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "input.csv"
    path.write_text(text, encoding="utf-8", newline="")
    return path


def test_valid_csv_is_converted_to_typed_records(tmp_path: Path) -> None:
    path = write_csv(tmp_path, HEADER + "101,Іваненко,2026-10-01,2026-10-04,1200.5\n")

    assert load_records(path) == [
        {
            "room": 101,
            "guest": "Іваненко",
            "check_in": date(2026, 10, 1),
            "check_out": date(2026, 10, 4),
            "rate": 1200.5,
            "nights": 3,
        }
    ]


def test_header_only_file_gives_empty_list(tmp_path: Path) -> None:
    assert load_records(write_csv(tmp_path, HEADER)) == []


def test_completely_empty_file_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(DataError, match="заголовка"):
        load_records(write_csv(tmp_path, ""))


def test_guest_with_comma_and_quotes_is_read_correctly(tmp_path: Path) -> None:
    text = HEADER + '102,"Коваль, ""Лі"" Олена",2026-10-02,2026-10-09,2000\n'

    records = load_records(write_csv(tmp_path, text))

    assert records[0]["guest"] == 'Коваль, "Лі" Олена'


def test_bad_number_reports_row_number_and_keeps_cause(tmp_path: Path) -> None:
    text = (
        HEADER + "101,А,2026-10-01,2026-10-04,1200\n102,Б,2026-10-01,2026-10-04,abc\n"
    )

    with pytest.raises(DataError, match="Рядок 3: поле rate") as info:
        load_records(write_csv(tmp_path, text))

    assert isinstance(info.value.__cause__, ValueError)


def test_missing_column_is_reported_with_its_name(tmp_path: Path) -> None:
    text = "room,guest,check_in,rate\n101,А,2026-10-01,1200\n"

    with pytest.raises(DataError, match="Відсутні стовпці: check_out"):
        load_records(write_csv(tmp_path, text))


def test_missing_value_in_short_row_names_row_and_field(tmp_path: Path) -> None:
    text = HEADER + "101,А,2026-10-01\n"

    with pytest.raises(DataError, match="Рядок 2: поле check_out") as info:
        load_records(write_csv(tmp_path, text))

    assert isinstance(info.value.__cause__, AttributeError)


def test_empty_guest_value_is_rejected(tmp_path: Path) -> None:
    text = HEADER + "101,  ,2026-10-01,2026-10-04,1200\n"

    with pytest.raises(DataError, match="Рядок 2: поле guest"):
        load_records(write_csv(tmp_path, text))


def test_bad_date_keeps_value_error_as_cause(tmp_path: Path) -> None:
    text = HEADER + "101,А,не-дата,2026-10-04,1200\n"

    with pytest.raises(DataError, match="Рядок 2: поле check_in") as info:
        load_records(write_csv(tmp_path, text))

    assert isinstance(info.value.__cause__, ValueError)


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ("0,А,2026-10-01,2026-10-04,1200", "room має бути додатним"),
        ("101,А,2026-10-04,2026-10-01,1200", "check_out має бути пізніше"),
        ("101,А,2026-10-01,2026-10-04,-5", "rate не може бути від'ємним"),
        ("abc,А,2026-10-01,2026-10-04,1200", "поле room має бути цілим"),
    ],
)
def test_forbidden_values_are_rejected(tmp_path: Path, row: str, message: str) -> None:
    with pytest.raises(DataError, match=message):
        load_records(write_csv(tmp_path, HEADER + row + "\n"))


def test_duplicate_rows_are_kept_as_separate_records(tmp_path: Path) -> None:
    row = "101,А,2026-10-01,2026-10-04,1200\n"

    assert len(load_records(write_csv(tmp_path, HEADER + row * 2))) == 2


def test_zero_rate_is_allowed(tmp_path: Path) -> None:
    records = load_records(
        write_csv(tmp_path, HEADER + "101,А,2026-10-01,2026-10-04,0\n")
    )

    assert records[0]["rate"] == 0.0
