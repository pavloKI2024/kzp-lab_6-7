"""Обчислення над бронюваннями через протокол Stay (качина типізація).

Модуль не перевіряє конкретні підтипи й не працює з файлами.
"""

from collections.abc import Sequence
from datetime import date

from kzp_lab07.models import ReportSummary, Stay


def active_bookings(bookings: Sequence[Stay], reference_date: date) -> list[Stay]:
    """Повертає бронювання, активні на задану дату."""
    return [booking for booking in bookings if booking.is_active_on(reference_date)]


def count_by_rate(bookings: Sequence[Stay]) -> dict[float, int]:
    """Рахує бронювання за тарифом; ключі йдуть за зростанням."""
    rates = {booking.rate for booking in bookings}
    return {
        rate: sum(1 for booking in bookings if booking.rate == rate)
        for rate in sorted(rates)
    }


def unique_guests(bookings: Sequence[Stay]) -> set[str]:
    """Повертає множину унікальних гостей."""
    return {booking.guest for booking in bookings}


def longest_stay(bookings: Sequence[Stay]) -> Stay | None:
    """Повертає найдовше проживання (перше за рівних) або None."""
    longest: Stay | None = None
    for booking in bookings:
        if longest is None or booking.nights > longest.nights:
            longest = booking
    return longest


def occupancy(bookings: Sequence[Stay], reference_date: date) -> tuple[int, int]:
    """Повертає пару (зайняті номери на дату, усього відомих номерів)."""
    all_rooms = {booking.room for booking in bookings}
    busy = {booking.room for booking in active_bookings(bookings, reference_date)}
    return len(busy), len(all_rooms)


def total_revenue(bookings: Sequence[Stay]) -> float:
    """Повертає суму вартостей проживання; формула залежить від підтипу."""
    return sum(booking.total_price() for booking in bookings)


def make_summary(bookings: Sequence[Stay], reference_date: date) -> ReportSummary:
    """Збирає підсумкові показники в незмінний ReportSummary."""
    busy, total = occupancy(bookings, reference_date)
    longest = longest_stay(bookings)
    return ReportSummary(
        reference_date=reference_date,
        count=len(bookings),
        active=len(active_bookings(bookings, reference_date)),
        busy_rooms=busy,
        total_rooms=total,
        guests=tuple(sorted(unique_guests(bookings))),
        rate_counts=tuple(count_by_rate(bookings).items()),
        longest_nights=None if longest is None else longest.nights,
        longest_guest=None if longest is None else longest.guest,
    )
