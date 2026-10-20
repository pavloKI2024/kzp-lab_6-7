"""Тести звіту й командного рядка."""

from datetime import date
from pathlib import Path

from kzp_lab06.analysis import make_summary
from kzp_lab06.cli import main
from kzp_lab06.reporting import format_report, write_report

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

    assert output.read_bytes() == "Готово\n".encode("utf-8")


def test_cli_success_writes_report_and_returns_zero(tmp_path: Path, capsys) -> None:
    output = tmp_path / "summary.txt"

    code = main(
        [
            str(ROOT / "data" / "input.csv"),
            str(output),
            "--reference-date",
            "2026-10-03",
        ]
    )

    text = output.read_text(encoding="utf-8")
    assert code == 0
    assert "Записів: 3" in text
    assert "Активних бронювань: 2" in text
    assert "Найдовше проживання: 7 ночей (Коваль, Олена)" in text
    assert capsys.readouterr().out == text


def test_cli_returns_nonzero_for_broken_csv(tmp_path: Path, capsys) -> None:
    broken = tmp_path / "broken.csv"
    broken.write_text("room,guest\n1,А\n", encoding="utf-8")

    code = main([str(broken), str(tmp_path / "out.txt")])

    assert code == 1
    assert "Відсутні стовпці" in capsys.readouterr().err
    assert not (tmp_path / "out.txt").exists()


def test_cli_returns_nonzero_for_missing_file(tmp_path: Path) -> None:
    assert main([str(tmp_path / "немає.csv"), str(tmp_path / "out.txt")]) == 2
