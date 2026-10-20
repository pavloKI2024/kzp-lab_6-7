"""Тести звіту й командного рядка ЛР7, а також сумісність зі звітом ЛР6."""

from datetime import date
from pathlib import Path

import pytest

from kzp_lab06.cli import main as main06
from kzp_lab07.analysis import make_summary
from kzp_lab07.cli import get_version, main
from kzp_lab07.reporting import format_report, write_report

ROOT = Path(__file__).resolve().parent.parent


def test_report_for_empty_input_is_deterministic() -> None:
    text = format_report(make_summary([], date(2026, 10, 3)))

    assert text == (
        "=== Звіт: Готель ===\n"
        "Дата: 2026-10-03\n"
        "Записів: 0\n"
        "Активних бронювань: 0\n"
        "Завантаження номерів: 0 з 0\n"
        "Найдовше проживання: немає даних\n"
        "Гості: немає\n"
        "Кількість за тарифом:\n"
    )


def test_write_report_creates_directory_and_uses_utf8(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "report.txt"

    write_report(output, "Готово\n")

    assert output.read_bytes() == "Готово\n".encode()


@pytest.mark.parametrize("csv_name", ["input.csv", "bookings.csv"])
def test_report_is_identical_to_previous_dictionary_version(
    tmp_path: Path, csv_name: str
) -> None:
    source = str(ROOT / "data" / csv_name)
    old, new = tmp_path / "old.txt", tmp_path / "new.txt"

    assert main06([source, str(old), "--reference-date", "2026-10-03"]) == 0
    assert main([source, str(new), "--reference-date", "2026-10-03"]) == 0

    assert new.read_bytes() == old.read_bytes()


def test_cli_success_with_revenue_line(tmp_path: Path, capsys) -> None:
    output = tmp_path / "summary.txt"

    code = main(
        [
            str(ROOT / "data" / "bookings.csv"),
            str(output),
            "--reference-date",
            "2026-10-03",
            "--with-revenue",
        ]
    )

    text = output.read_text(encoding="utf-8")
    assert code == 0
    assert "Записів: 7" in text
    assert text.endswith("Виторг: 59029.50\n")
    assert capsys.readouterr().out == text


def test_cli_returns_nonzero_for_broken_csv(tmp_path: Path, capsys) -> None:
    broken = tmp_path / "broken.csv"
    broken.write_text("room,guest\n1,А\n", encoding="utf-8")

    code = main([str(broken), str(tmp_path / "out.txt")])

    assert code == 1
    assert "Відсутні стовпці" in capsys.readouterr().err
    assert not (tmp_path / "out.txt").exists()


def test_cli_returns_nonzero_for_bad_row_with_row_number(
    tmp_path: Path, capsys
) -> None:
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "room,guest,check_in,check_out,rate\n1,А,2026-10-01,2026-10-04,-1\n",
        encoding="utf-8",
    )

    assert main([str(bad), str(tmp_path / "out.txt")]) == 1
    assert "Рядок 2" in capsys.readouterr().err


def test_cli_returns_nonzero_for_missing_file(tmp_path: Path) -> None:
    assert main([str(tmp_path / "немає.csv"), str(tmp_path / "out.txt")]) == 2


def test_cli_does_not_modify_input(tmp_path: Path) -> None:
    source = ROOT / "data" / "bookings.csv"
    before = source.read_bytes()

    main([str(source), str(tmp_path / "out.txt"), "--reference-date", "2026-10-03"])

    assert source.read_bytes() == before


def test_cli_version_comes_from_package_metadata(capsys) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"kzp-lab07 {get_version()}"
