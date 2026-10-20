"""Тести об'єктної моделі: властивості, рівність, підтипи, dataclass."""

import dataclasses
from datetime import date

import pytest

from kzp_lab07.models import (
    PREMIUM_RATE_FROM,
    PREMIUM_SURCHARGE,
    Booking,
    PremiumBooking,
    ReportSummary,
    StandardBooking,
    make_booking,
)

IN = date(2026, 10, 1)
OUT = date(2026, 10, 4)


def standard(rate: float = 1000.0) -> StandardBooking:
    return StandardBooking(101, "Іваненко", IN, OUT, rate)


def test_properties_return_constructor_values() -> None:
    booking = standard(1200.5)

    assert (booking.room, booking.guest, booking.rate) == (101, "Іваненко", 1200.5)
    assert (booking.check_in, booking.check_out, booking.nights) == (IN, OUT, 3)


def test_guest_is_stripped_by_setter() -> None:
    booking = standard()
    booking.guest = "  Коваль  "

    assert booking.guest == "Коваль"


@pytest.mark.parametrize("value", [0, -1])
def test_room_setter_rejects_non_positive(value: int) -> None:
    booking = standard()

    with pytest.raises(ValueError, match="room"):
        booking.room = value
    assert booking.room == 101


def test_room_setter_accepts_boundary_value_one() -> None:
    booking = standard()
    booking.room = 1

    assert booking.room == 1


def test_rate_setter_boundary_zero_is_allowed_negative_is_not() -> None:
    booking = standard()
    booking.rate = 0

    assert booking.rate == 0.0
    with pytest.raises(ValueError, match="rate"):
        booking.rate = -0.01
    with pytest.raises(ValueError, match="rate"):
        booking.rate = float("nan")


def test_empty_guest_is_rejected() -> None:
    with pytest.raises(ValueError, match="guest"):
        StandardBooking(1, "  ", IN, OUT, 1)


def test_checkout_must_be_after_checkin() -> None:
    with pytest.raises(ValueError, match="check_out"):
        StandardBooking(1, "А", OUT, IN, 1)
    with pytest.raises(ValueError, match="check_out"):
        StandardBooking(1, "А", IN, IN, 1)


def test_dates_are_read_only() -> None:
    with pytest.raises(AttributeError):
        standard().check_in = OUT  # type: ignore[misc]


def test_is_active_includes_checkin_and_excludes_checkout() -> None:
    booking = standard()

    assert booking.is_active_on(IN)
    assert not booking.is_active_on(OUT)
    assert not booking.is_active_on(date(2026, 9, 30))


def test_equal_bookings_with_same_type_and_fields_are_equal() -> None:
    assert standard(1000.0) == standard(1000.0)
    assert standard(1000.0) != standard(1001.0)


def test_same_fields_but_different_subtypes_are_not_equal() -> None:
    assert StandardBooking(1, "А", IN, OUT, 5) != PremiumBooking(1, "А", IN, OUT, 5)


def test_eq_returns_notimplemented_for_other_types() -> None:
    assert standard().__eq__("текст") is NotImplemented
    assert standard() != "текст"


def test_bookings_are_unhashable_because_state_is_mutable() -> None:
    with pytest.raises(TypeError):
        hash(standard())


def test_sorting_uses_checkin_then_room() -> None:
    late = StandardBooking(1, "А", date(2026, 10, 5), date(2026, 10, 6), 1)
    early_high = StandardBooking(9, "Б", IN, OUT, 1)
    early_low = StandardBooking(2, "В", IN, OUT, 1)

    assert sorted([late, early_high, early_low]) == [early_low, early_high, late]


def test_str_and_repr() -> None:
    booking = standard(1200.5)

    assert str(booking) == "Кімната 101: Іваненко, 2026-10-01 — 2026-10-04, 3 ночей"
    assert repr(booking) == (
        "StandardBooking(room=101, guest='Іваненко', "
        "check_in=datetime.date(2026, 10, 1), "
        "check_out=datetime.date(2026, 10, 4), rate=1200.5)"
    )


def test_subtypes_have_different_prices_for_same_data() -> None:
    standard_price = StandardBooking(1, "А", IN, OUT, 1000).total_price()
    premium_price = PremiumBooking(1, "А", IN, OUT, 1000).total_price()

    assert standard_price == 3000.0
    assert premium_price == pytest.approx(3000.0 * PREMIUM_SURCHARGE)


def test_base_total_price_is_abstract() -> None:
    with pytest.raises(NotImplementedError):
        Booking(1, "А", IN, OUT, 1).total_price()


def test_make_booking_chooses_subtype_by_rate_threshold() -> None:
    assert (
        type(make_booking(1, "А", IN, OUT, PREMIUM_RATE_FROM - 0.01)) is StandardBooking
    )
    assert type(make_booking(1, "А", IN, OUT, PREMIUM_RATE_FROM)) is PremiumBooking


def test_summary_is_immutable_and_comparable() -> None:
    summary = ReportSummary(IN, 1, 1, 1, 1, ("А",), ((1.0, 1),), 3, "А")

    with pytest.raises(dataclasses.FrozenInstanceError):
        summary.count = 2  # type: ignore[misc]
    assert summary == dataclasses.replace(summary)
    assert summary != dataclasses.replace(summary, count=2)
