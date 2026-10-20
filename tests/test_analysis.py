"""Тести функцій аналізу."""

from datetime import date

import pytest

from kzp_lab06.analysis import (
    active_bookings,
    count_by_rate,
    longest_stay,
    make_summary,
    occupancy,
    summarize,
    unique_guests,
)


def booking(room: int, guest: str, check_in: str, check_out: str, rate: float) -> dict:
    start, end = date.fromisoformat(check_in), date.fromisoformat(check_out)
    return {
        "room": room,
        "guest": guest,
        "check_in": start,
        "check_out": end,
        "rate": rate,
        "nights": (end - start).days,
    }


RECORDS = [
    booking(101, "А", "2026-10-01", "2026-10-04", 1200.5),
    booking(102, "Б", "2026-10-02", "2026-10-09", 2000.0),
    booking(103, "А", "2026-10-05", "2026-10-07", 1200.5),
]


def test_active_bookings_include_checkin_and_exclude_checkout() -> None:
    assert [r["room"] for r in active_bookings(RECORDS, date(2026, 10, 1))] == [101]
    assert [r["room"] for r in active_bookings(RECORDS, date(2026, 10, 4))] == [102]


def test_count_by_rate_is_sorted_and_counts_duplicates() -> None:
    assert count_by_rate(RECORDS) == {1200.5: 2, 2000.0: 1}
    assert list(count_by_rate(RECORDS)) == [1200.5, 2000.0]


def test_unique_guests_removes_duplicates() -> None:
    assert unique_guests(RECORDS) == {"А", "Б"}


def test_longest_stay_takes_first_on_tie() -> None:
    tie = [
        booking(1, "А", "2026-10-01", "2026-10-03", 1),
        booking(2, "Б", "2026-10-05", "2026-10-07", 1),
    ]

    assert longest_stay(RECORDS)["room"] == 102
    assert longest_stay(tie)["room"] == 1


def test_occupancy_counts_distinct_rooms() -> None:
    assert occupancy(RECORDS, date(2026, 10, 3)) == (2, 3)


def test_empty_input_gives_empty_results() -> None:
    today = date(2026, 10, 3)

    assert active_bookings([], today) == []
    assert count_by_rate([]) == {}
    assert unique_guests([]) == set()
    assert longest_stay([]) is None
    assert occupancy([], today) == (0, 0)
    assert make_summary([], today)["count"] == 0


def test_summarize_with_defaults_args_and_kwargs() -> None:
    result = summarize(RECORDS, "nights", "rate", minimum_nights=3, nights="Ночі")

    assert result == {"count": 2, "Ночі": 10.0, "rate": 3200.5}


def test_summarize_unknown_metric_is_rejected() -> None:
    with pytest.raises(ValueError, match="Невідома метрика"):
        summarize(RECORDS, "colour")


def test_summarize_filtered_out_everything_gives_zero() -> None:
    assert summarize(RECORDS, "nights", minimum_nights=100) == {
        "count": 0,
        "nights": 0.0,
    }
