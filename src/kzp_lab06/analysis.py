"""Обчислення над типізованими записами. Модуль не працює з файлами."""

from datetime import date

from kzp_lab06.loader import Record


def active_bookings(records: list[Record], reference_date: date) -> list[Record]:
    """Повертає бронювання, активні на задану дату (заїзд включно, виїзд ні)."""
    return [
        record
        for record in records
        if record["check_in"] <= reference_date < record["check_out"]
    ]


def count_by_rate(records: list[Record]) -> dict[float, int]:
    """Рахує бронювання за тарифом; ключі йдуть за зростанням."""
    rates = {float(record["rate"]) for record in records}
    return {
        rate: sum(1 for record in records if record["rate"] == rate)
        for rate in sorted(rates)
    }


def unique_guests(records: list[Record]) -> set[str]:
    """Повертає множину унікальних гостей."""
    return {str(record["guest"]) for record in records}


def longest_stay(records: list[Record]) -> Record | None:
    """Повертає найдовше проживання (перше за рівних) або None для порожнього входу."""
    longest: Record | None = None
    for record in records:
        if longest is None or record["nights"] > longest["nights"]:
            longest = record
    return longest


def occupancy(records: list[Record], reference_date: date) -> tuple[int, int]:
    """Повертає пару (зайняті номери на дату, усього відомих номерів)."""
    all_rooms = {record["room"] for record in records}
    busy_rooms = {record["room"] for record in active_bookings(records, reference_date)}
    return len(busy_rooms), len(all_rooms)


def summarize(
    records: list[Record],
    *metrics: str,
    minimum_nights: int = 0,
    **labels: str,
) -> dict[str, object]:
    """Обчислює суми вибраних числових метрик для записів від minimum_nights ночей.

    metrics — назви числових полів запису; labels задають підписи метрик.
    Для порожнього відбору визначені метрики дорівнюють 0.0.
    """
    selected = [record for record in records if record["nights"] >= minimum_nights]
    result: dict[str, object] = {"count": len(selected)}
    for metric in metrics:
        if records and any(metric not in record for record in records):
            raise ValueError(f"Невідома метрика: {metric}")
        result[labels.get(metric, metric)] = sum(
            float(record[metric]) for record in selected
        )
    return result


def make_summary(records: list[Record], reference_date: date) -> dict[str, object]:
    """Збирає всі показники звіту в один словник."""
    busy, total = occupancy(records, reference_date)
    return {
        "reference_date": reference_date,
        "count": len(records),
        "active": len(active_bookings(records, reference_date)),
        "guests": sorted(unique_guests(records)),
        "rate_counts": count_by_rate(records),
        "busy_rooms": busy,
        "total_rooms": total,
        "longest": longest_stay(records),
    }
