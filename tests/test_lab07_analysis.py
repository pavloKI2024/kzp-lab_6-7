"""Тести аналізу через протокол Stay, зокрема качина типізація."""

from datetime import date

import pytest

from kzp_lab07.analysis import (
    active_bookings,
    count_by_rate,
    longest_stay,
    make_summary,
    occupancy,
    total_revenue,
    unique_guests,
)
from kzp_lab07.models import PremiumBooking, StandardBooking

D = date.fromisoformat

BOOKINGS = [
    StandardBooking(101, "А", D("2026-10-01"), D("2026-10-04"), 1200.5),
    PremiumBooking(102, "Б", D("2026-10-02"), D("2026-10-09"), 2000.0),
    StandardBooking(103, "А", D("2026-10-05"), D("2026-10-07"), 1200.5),
]


class FakeStay:
    """Не є підтипом Booking, але має потрібні методи (качина типізація)."""

    room = 7
    guest = "Качка"
    rate = 10.0
    nights = 2

    def is_active_on(self, day: date) -> bool:
        return True

    def total_price(self) -> float:
        return 99.0


def test_active_bookings_work_through_protocol() -> None:
    assert [b.room for b in active_bookings(BOOKINGS, D("2026-10-03"))] == [101, 102]


def test_count_by_rate_is_sorted_and_counts_duplicates() -> None:
    assert count_by_rate(BOOKINGS) == {1200.5: 2, 2000.0: 1}


def test_unique_guests_removes_duplicates() -> None:
    assert unique_guests(BOOKINGS) == {"А", "Б"}


def test_longest_stay_takes_first_on_tie() -> None:
    tie = [
        StandardBooking(1, "А", D("2026-10-01"), D("2026-10-03"), 1),
        StandardBooking(2, "Б", D("2026-10-05"), D("2026-10-07"), 1),
    ]

    assert longest_stay(BOOKINGS).room == 102
    assert longest_stay(tie).room == 1


def test_occupancy_counts_distinct_rooms() -> None:
    assert occupancy(BOOKINGS, D("2026-10-03")) == (2, 3)


def test_total_revenue_uses_each_subtype_formula() -> None:
    expected = 3 * 1200.5 + 7 * 2000.0 * 1.15 + 2 * 1200.5

    assert total_revenue(BOOKINGS) == pytest.approx(expected)


def test_analysis_accepts_any_object_with_the_protocol() -> None:
    fake = FakeStay()

    assert total_revenue([fake]) == 99.0
    assert longest_stay([fake]) is fake
    assert unique_guests([fake]) == {"Качка"}
    assert make_summary([fake], D("2026-10-03")).count == 1


def test_empty_input_gives_empty_results() -> None:
    day = D("2026-10-03")

    assert active_bookings([], day) == []
    assert count_by_rate([]) == {}
    assert unique_guests([]) == set()
    assert longest_stay([]) is None
    assert occupancy([], day) == (0, 0)
    assert total_revenue([]) == 0
    summary = make_summary([], day)
    assert (summary.count, summary.longest_nights, summary.guests) == (0, None, ())


def test_summary_contains_expected_values() -> None:
    summary = make_summary(BOOKINGS, D("2026-10-03"))

    assert summary.count == 3
    assert summary.active == 2
    assert (summary.busy_rooms, summary.total_rooms) == (2, 3)
    assert summary.guests == ("А", "Б")
    assert summary.rate_counts == ((1200.5, 2), (2000.0, 1))
    assert (summary.longest_nights, summary.longest_guest) == (7, "Б")
