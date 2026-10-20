"""Формування та запис текстового звіту. Модуль не читає CSV."""

from pathlib import Path


def format_report(summary: dict[str, object]) -> str:
    """Форматує підсумок у детермінований текстовий звіт."""
    lines = [
        "=== Звіт: Готель ===",
        f"Дата: {summary['reference_date']}",
        f"Записів: {summary['count']}",
        f"Активних бронювань: {summary['active']}",
        f"Завантаження номерів: {summary['busy_rooms']} з {summary['total_rooms']}",
    ]
    longest = summary["longest"]
    if longest is None:
        lines.append("Найдовше проживання: немає даних")
    else:
        lines.append(
            f"Найдовше проживання: {longest['nights']} ночей ({longest['guest']})"
        )
    lines.append("Гості: " + ("; ".join(summary["guests"]) or "немає"))
    lines.append("Кількість за тарифом:")
    for rate, count in summary["rate_counts"].items():
        lines.append(f"  {rate:.2f}: {count}")
    return "\n".join(lines) + "\n"


def write_report(path: Path, text: str) -> None:
    """Записує текстовий звіт у файл UTF-8, створюючи каталог за потреби."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # with гарантує закриття файла навіть у разі помилки запису.
    with path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(text)
