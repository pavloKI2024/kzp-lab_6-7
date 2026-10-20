"""Формування та запис текстового звіту. Модуль не читає CSV."""

from pathlib import Path

from kzp_lab07.models import ReportSummary


def format_report(summary: ReportSummary, revenue: float | None = None) -> str:
    """Форматує підсумок у детермінований текстовий звіт.

    Формат збігається зі звітом попередньої роботи. Якщо передано revenue,
    наприкінці додається рядок «Виторг».
    """
    lines = [
        "=== Звіт: Готель ===",
        f"Дата: {summary.reference_date}",
        f"Записів: {summary.count}",
        f"Активних бронювань: {summary.active}",
        f"Завантаження номерів: {summary.busy_rooms} з {summary.total_rooms}",
    ]
    if summary.longest_nights is None:
        lines.append("Найдовше проживання: немає даних")
    else:
        lines.append(
            f"Найдовше проживання: {summary.longest_nights} ночей "
            f"({summary.longest_guest})"
        )
    lines.append("Гості: " + ("; ".join(summary.guests) or "немає"))
    lines.append("Кількість за тарифом:")
    for rate, count in summary.rate_counts:
        lines.append(f"  {rate:.2f}: {count}")
    if revenue is not None:
        lines.append(f"Виторг: {revenue:.2f}")
    return "\n".join(lines) + "\n"


def write_report(path: Path, text: str) -> None:
    """Записує текстовий звіт у файл UTF-8, створюючи каталог за потреби."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # with гарантує закриття файла навіть у разі помилки запису.
    with path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(text)
