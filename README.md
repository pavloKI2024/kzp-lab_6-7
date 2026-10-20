# kzp-lab_6-7

У репозиторії дві лабораторні роботи: № 6 (пакет `kzp_lab06`) і № 7 (пакет `kzp_lab07`, див. розділ «Лабораторна робота № 7»).

Лабораторна робота № 6 з курсу «Кросплатформні засоби програмування» — обробка даних засобами Python. Варіант 14 — **Готель**.

## Призначення

Python-пакет читає CSV із бронюваннями (це CSV, експортований Java-застосунком у ЛР5), перетворює поля на типізовані значення, будує звіт і записує його у текстовий файл UTF-8:

- відбір — бронювання, активні на `reference_date` (заїзд включно, виїзд ні);
- словник — кількість бронювань за тарифом;
- множина — унікальні гості;
- звіт — завантаження номерів і найдовше проживання.

## Формат входу

`data/input.csv`, UTF-8, перший рядок — заголовок:

```
room,guest,check_in,check_out,rate
101,Іваненко Петро,2026-10-01,2026-10-04,1200.5
102,"Коваль, Олена",2026-10-02,2026-10-09,2000.0
103,"Бондар ""Макс"" Максим",2026-10-05,2026-10-07,850.0
```

| Поле | Тип | Правило |
|------|-----|---------|
| room | int | більше 0 |
| guest | str | не порожнє |
| check_in, check_out | date | `YYYY-MM-DD`, виїзд пізніше за заїзд |
| rate | float | не менше 0 |

Файл лише із заголовком — коректний порожній набір (звіт із нулями). Файл без заголовка або без обов'язкових стовпців — помилка `DataError`.

## Структура

```
src/kzp_lab06/
├── __init__.py   — публічний API (DataError)
├── errors.py     — DataError
├── loader.py     — читання CSV через csv.DictReader та перетворення типів
├── analysis.py   — відбір, словник, множина, summarize(*args, **kwargs)
├── reporting.py  — формування й запис звіту
└── cli.py        — аргументи командного рядка, коди завершення
tests/            — pytest
data/input.csv    — вхідні дані
reports/          — вихідні звіти (не додаються до репозиторію)
```

## Запуск

Потрібен Python 3.11 або новіший.

```
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate        # macOS, Ubuntu
python -m pip install -e ".[dev]"

python -m kzp_lab06.cli data/input.csv reports/summary.txt --reference-date 2026-10-03
python -m pytest
ruff check .
ruff format --check .
```

### Збирання wheel і встановлення в чисте середовище

```
python -m build                                     # dist/kzp_lab06-2.0.0-py3-none-any.whl
python -m venv .venv-wheel
.venv-wheel\Scripts\python -m pip install --no-deps dist\kzp_lab06-2.0.0-py3-none-any.whl   # Windows
.venv-wheel/bin/python -m pip install --no-deps dist/kzp_lab06-2.0.0-py3-none-any.whl          # macOS, Ubuntu
.venv-wheel/bin/python -m kzp_lab06.cli data/input.csv reports/wheel-summary.txt --reference-date 2026-10-03
kzp-lab06 data/input.csv reports/summary.txt        # встановлена команда
```

### CI і версія

GitHub Actions (`.github/workflows/ci.yml`) на Ubuntu, Windows і macOS виконує `pytest`, `ruff check`, `ruff format --check`, збирає wheel, встановлює його в чисте середовище, перевіряє CLI (успіх — код 0, відсутній файл — код 2, пошкоджений CSV — код 1) і публікує wheel як артефакт.

Версія зберігається лише в `pyproject.toml` (поточна — `2.0.0`); `kzp-lab06 --version` читає її з метаданих встановленого пакета. Git-тег має збігатися з нею: `v2.0.0`.

Без `--reference-date` береться сьогоднішня дата. Коди завершення: `0` — успіх, `1` — помилка даних (повідомлення в stderr), `2` — помилка файлу.

## Приклад звіту

```
=== Звіт: Готель ===
Дата: 2026-10-03
Записів: 3
Активних бронювань: 2
Завантаження номерів: 2 з 3
Найдовше проживання: 7 ночей (Коваль, Олена)
Гості: Іваненко Петро; Бондар "Макс" Максим; Коваль, Олена
Кількість за тарифом:
  850.00: 1
  1200.50: 1
  2000.00: 1
```

## Лабораторна робота № 7 — об'єктна модель (`kzp_lab07`)

Той самий CSV і той самий звіт, але записи — об'єкти, а не словники. Формат звіту збігається зі звітом ЛР6 побайтово (це перевіряє тест).

```
src/kzp_lab07/
├── models.py     — Booking (@property + setter), StandardBooking, PremiumBooking,
│                   Protocol Stay, @dataclass(frozen=True) ReportSummary
├── loader.py     — CSV → об'єкти, DataError із номером рядка та першопричиною
├── analysis.py   — запити через протокол Stay, без перевірок підтипу
├── reporting.py  — текстовий звіт
├── errors.py     — DataError
└── cli.py        — аргументи та коди завершення
data/bookings.csv — 7 записів: обидва підтипи, дубльований запис, лапки й кома
```

### Модель

- `Booking` — базовий клас: властивості `room`, `guest`, `rate` із перевірками в setter, незмінні `check_in`/`check_out`, `nights`, `is_active_on(day)`; методи `__str__`, `__repr__`, `__eq__` (за типом і полями), `__lt__` (за датою заїзду, потім номером), `__hash__ = None` (стан змінюваний).
- `StandardBooking.total_price()` = ночі × тариф; `PremiumBooking.total_price()` = ночі × тариф × 1.15 (надбавка).
- Підтип вибирає `make_booking`: тариф від 2000 — преміальний, бо в CSV немає окремого поля типу.
- `Stay` — `Protocol`: `analysis` працює з будь-яким об'єктом, що має ці властивості й методи (качина типізація), і не перевіряє конкретні класи.
- `ReportSummary` — незмінний `@dataclass(frozen=True)` із підсумком.

### Запуск

```
python -m kzp_lab07.cli data/bookings.csv reports/summary7.txt --reference-date 2026-10-03
python -m kzp_lab07.cli data/bookings.csv reports/summary7.txt --reference-date 2026-10-03 --with-revenue
kzp-lab07 data/bookings.csv reports/summary7.txt
```

`--with-revenue` додає в кінець звіту рядок `Виторг` (сума `total_price()` підтипів); без нього звіт такий самий, як у ЛР6. Коди завершення: `0`, `1` (помилка даних), `2` (помилка файлу).
