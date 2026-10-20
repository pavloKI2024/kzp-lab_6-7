"""Об'єктна модель: сутність бронювання, підтипи, протокол і підсумок.

Модуль не читає файлів і не формує звіт.
"""

import math
from dataclasses import dataclass
from datetime import date
from typing import Protocol

# Кімнати з тарифом від цього значення вважаються преміальними.
PREMIUM_RATE_FROM = 2000.0
# Надбавка преміального бронювання до вартості проживання.
PREMIUM_SURCHARGE = 1.15


class Stay(Protocol):
    """Протокол бронювання: усе, що потрібно функціям аналізу."""

    @property
    def room(self) -> int:
        """Повертає номер кімнати."""
        ...

    @property
    def guest(self) -> str:
        """Повертає ім'я гостя."""
        ...

    @property
    def rate(self) -> float:
        """Повертає тариф за ніч."""
        ...

    @property
    def nights(self) -> int:
        """Повертає кількість ночей."""
        ...

    def is_active_on(self, day: date) -> bool:
        """Перевіряє, чи активне бронювання на дату."""
        ...

    def total_price(self) -> float:
        """Повертає вартість проживання."""
        ...


class Booking:
    """Базове бронювання зі спільним станом та інваріантами."""

    def __init__(
        self, room: int, guest: str, check_in: date, check_out: date, rate: float
    ) -> None:
        """Створює бронювання та перевіряє початкові дані."""
        if check_out <= check_in:
            raise ValueError("check_out має бути пізніше за check_in")
        self._check_in = check_in
        self._check_out = check_out
        # Присвоєння йде через властивості, тому перевірка виконується в setter.
        self.room = room
        self.guest = guest
        self.rate = rate

    @property
    def room(self) -> int:
        """Повертає номер кімнати."""
        return self._room

    @room.setter
    def room(self, value: int) -> None:
        """Встановлює додатний номер кімнати."""
        if value <= 0:
            raise ValueError("room має бути додатним")
        self._room = value

    @property
    def guest(self) -> str:
        """Повертає ім'я гостя."""
        return self._guest

    @guest.setter
    def guest(self, value: str) -> None:
        """Встановлює непорожнє ім'я гостя без пробілів по краях."""
        name = value.strip()
        if not name:
            raise ValueError("guest не може бути порожнім")
        self._guest = name

    @property
    def rate(self) -> float:
        """Повертає тариф за ніч."""
        return self._rate

    @rate.setter
    def rate(self, value: float) -> None:
        """Встановлює скінченний невід'ємний тариф."""
        if value < 0 or not math.isfinite(value):
            raise ValueError("rate не може бути від'ємним")
        self._rate = float(value)

    @property
    def check_in(self) -> date:
        """Повертає дату заїзду (незмінна)."""
        return self._check_in

    @property
    def check_out(self) -> date:
        """Повертає дату виїзду (незмінна)."""
        return self._check_out

    @property
    def nights(self) -> int:
        """Повертає кількість ночей."""
        return (self._check_out - self._check_in).days

    def is_active_on(self, day: date) -> bool:
        """Перевіряє активність на дату: заїзд включно, виїзд ні."""
        return self._check_in <= day < self._check_out

    def total_price(self) -> float:
        """Оголошує вартість проживання; формулу реалізують підтипи."""
        raise NotImplementedError

    def _key(self) -> tuple[object, ...]:
        """Повертає кортеж полів, за яким порівнюються бронювання."""
        return (self._room, self._guest, self._check_in, self._check_out, self._rate)

    def __str__(self) -> str:
        """Повертає коротке подання для читача."""
        return (
            f"Кімната {self.room}: {self.guest}, "
            f"{self.check_in} — {self.check_out}, {self.nights} ночей"
        )

    def __repr__(self) -> str:
        """Повертає діагностичне подання об'єкта."""
        return (
            f"{type(self).__name__}(room={self.room!r}, guest={self.guest!r}, "
            f"check_in={self.check_in!r}, check_out={self.check_out!r}, "
            f"rate={self.rate!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Порівнює за типом і всіма полями."""
        if not isinstance(other, Booking):
            return NotImplemented
        return type(self) is type(other) and self._key() == other._key()

    # Стан змінюваний, тому об'єкт не можна використовувати як ключ словника.
    __hash__ = None  # type: ignore[assignment]

    def __lt__(self, other: object) -> bool:
        """Впорядковує за датою заїзду, потім за номером кімнати."""
        if not isinstance(other, Booking):
            return NotImplemented
        return (self.check_in, self.room) < (other.check_in, other.room)


class StandardBooking(Booking):
    """Стандартне бронювання: вартість — ночі, помножені на тариф."""

    def total_price(self) -> float:
        """Повертає вартість проживання без надбавки."""
        return self.nights * self.rate


class PremiumBooking(Booking):
    """Преміальне бронювання: до вартості додається надбавка."""

    def total_price(self) -> float:
        """Повертає вартість проживання з надбавкою PREMIUM_SURCHARGE."""
        return self.nights * self.rate * PREMIUM_SURCHARGE


def make_booking(
    room: int, guest: str, check_in: date, check_out: date, rate: float
) -> Booking:
    """Створює підтип за тарифом: від PREMIUM_RATE_FROM — преміальне."""
    kind = PremiumBooking if rate >= PREMIUM_RATE_FROM else StandardBooking
    return kind(room, guest, check_in, check_out, rate)


@dataclass(frozen=True)
class ReportSummary:
    """Незмінні підсумкові показники звіту."""

    reference_date: date
    count: int
    active: int
    busy_rooms: int
    total_rooms: int
    guests: tuple[str, ...]
    rate_counts: tuple[tuple[float, int], ...]
    longest_nights: int | None
    longest_guest: str | None
