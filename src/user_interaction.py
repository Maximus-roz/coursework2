"""Консольный интерфейс для работы с самолётами.

Поддерживает два хранилища:
  - файловое (JSON) — через JSONStorage;
  - PostgreSQL       — через DBManager / DBFiller.

Меню разбито на два блока: файловое хранилище (пункты 1–7)
и работа с БД (пункты 8–14).
"""

from request_api import APIAdapter
from aeroplanes_info import Aeroplane
from json_storage import JSONStorage
from config import TRACKED_COUNTRIES
from db_manager import DBManager
from db_filler import DBFiller


# ---------------------------------------------------------------------------
# Утилиты ввода
# ---------------------------------------------------------------------------

def _safe_input(prompt: str) -> str:
    """input() с защитой от Ctrl+C / Ctrl+D — не роняем программу."""
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nВыход.")
        raise SystemExit(0)


def _ask_int(prompt: str, default: int = 10, minimum: int = 1) -> int:
    """Спрашивает целое число с валидацией. Пустой ввод → default."""
    while True:
        raw = _safe_input(prompt)
        if not raw:
            return default
        try:
            value = int(raw)
            if value < minimum:
                print(f"Введите число не меньше {minimum}.")
                continue
            return value
        except ValueError:
            print("Нужно целое число. Попробуйте ещё раз.")


def _ask_float_or_none(prompt: str):
    """Спрашивает число или возвращает None при пустом вводе."""
    raw = _safe_input(prompt)
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        print(f"«{raw}» — не число, критерий пропущен.")
        return None


# ---------------------------------------------------------------------------
# Печать таблиц
# ---------------------------------------------------------------------------

def _print_table(records: list, limit: int = None) -> None:
    """Печатает список записей (dict из файлового хранилища) в виде таблицы."""
    if not records:
        print("Ничего не найдено.")
        return

    if limit is not None:
        records = records[:limit]

    header = f"{'Позывной':<10} {'Страна':<20} {'Скорость, м/с':>13} {'Высота, м':>10}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    for rec in records:
        callsign = rec.get("callsign") or "Unknown"
        country = rec.get("origin_country") or "?"
        velocity = rec.get("velocity")
        altitude = rec.get("baro_altitude")
        v_str = f"{velocity:.1f}" if velocity is not None else "—"
        a_str = f"{altitude:.0f}" if altitude is not None else "—"
        print(f"{callsign:<10} {country:<20} {v_str:>13} {a_str:>10}")
    print("-" * len(header))
    print(f"Всего: {len(records)}")


def _print_db_table(rows: list, columns: list, headers: list) -> None:
    """Печатает произвольный SQL-результат (list[dict]) в виде таблицы."""
    if not rows:
        print("Ничего не найдено.")
        return

    # ширины колонок = максимум из (заголовок, значения)
    widths = []
    for col, hdr in zip(columns, headers):
        values = [str(r.get(col, "")) if r.get(col) is not None else "—" for r in rows]
        widths.append(max(len(hdr), *(len(v) for v in values)))

    line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(line)
    print("-" * len(line))
    for r in rows:
        cells = []
        for col, w in zip(columns, widths):
            val = r.get(col)
            cells.append(("—" if val is None else str(val)).ljust(w))
        print(" | ".join(cells))
    print(f"\nВсего: {len(rows)}")


# ---------------------------------------------------------------------------
# Файловое хранилище (пункты 1–7)
# ---------------------------------------------------------------------------

def _load_aeroplanes(storage: JSONStorage) -> None:
    """Запрашивает страну у пользователя и сохраняет самолёты в файл."""
    country = _safe_input("Введите название страны (например, italia): ")
    if not country:
        print("Название страны не может быть пустым.")
        return

    print(f"Запрашиваю данные для «{country}»…")
    api = APIAdapter()
    try:
        response = api.get_aeroplanes(country)
    except ValueError as e:
        print(f"Ошибка: {e}")
        return
    except Exception as e:
        print(f"Не удалось получить данные: {e}")
        return

    states = response.get("states") or []
    if not states:
        print("В воздушном пространстве этой страны самолётов не найдено.")
        return

    added = 0
    for state in states:
        if len(state) < 10:
            continue
        try:
            plane = Aeroplane(
                callsign=state[1],
                origin_country=state[2],
                velocity=state[9],
                baro_altitude=state[7],
            )
        except (TypeError, ValueError):
            continue
        storage.add_aeroplane(plane)
        added += 1

    print(f"Сохранено самолётов: {added} из {len(states)}.")


def _top_by_altitude(storage: JSONStorage) -> None:
    n = _ask_int("Сколько самолётов показать (N)? [по умолчанию 10]: ")
    records = storage.get_all()
    valid = [r for r in records if r.get("baro_altitude") is not None]
    valid.sort(key=lambda r: r["baro_altitude"], reverse=True)
    _print_table(valid, limit=n)


def _top_by_velocity(storage: JSONStorage) -> None:
    n = _ask_int("Сколько самолётов показать (N)? [по умолчанию 10]: ")
    records = storage.get_all()
    valid = [r for r in records if r.get("velocity") is not None]
    valid.sort(key=lambda r: r["velocity"], reverse=True)
    _print_table(valid, limit=n)


def _filter_by_country(storage: JSONStorage) -> None:
    country = _safe_input("Введите страну регистрации: ")
    if not country:
        print("Страна не может быть пустой.")
        return
    records = storage.get_aeroplanes(origin_country=country)
    _print_table(records)


def _filter_by_altitude_range(storage: JSONStorage) -> None:
    print("Оставьте поле пустым, чтобы не задавать границу.")
    min_alt = _ask_float_or_none("Минимальная высота, м: ")
    max_alt = _ask_float_or_none("Максимальная высота, м: ")
    criteria = {}
    if min_alt is not None:
        criteria["min_baro_altitude"] = min_alt
    if max_alt is not None:
        criteria["max_baro_altitude"] = max_alt
    if not criteria:
        print("Ни одной границы не задано — показываю всё.")
    records = storage.get_aeroplanes(**criteria)
    _print_table(records)


def _clear_storage(storage: JSONStorage) -> None:
    confirm = _safe_input("Удалить все сохранённые данные? (y/n): ").lower()
    if confirm == "y":
        storage.clear()
        print("Хранилище очищено.")
    else:
        print("Отменено.")


# ---------------------------------------------------------------------------
# PostgreSQL (пункты 8–14)
# ---------------------------------------------------------------------------

def _fill_db() -> None:
    """Создаёт таблицы и заполняет БД данными 4 стран."""
    print("Страны для отслеживания:", ", ".join(TRACKED_COUNTRIES))
    confirm = _safe_input("Создать таблицы и загрузить данные? (y/n): ").lower()
    if confirm != "y":
        print("Отменено.")
        return

    filler = DBFiller()
    try:
        filler.create_tables()
        stats = filler.fill_tracked_countries()
    except Exception as e:
        print(f"Ошибка БД: {e}")
        return

    print("\nИтого по странам:")
    for country, cnt in stats.items():
        print(f"  {country:<12} — {cnt}")


def _db_countries_stats() -> None:
    rows = DBManager().get_countries_and_aeroplanes_count()
    _print_db_table(
        rows,
        columns=["country", "aeroplanes_count"],
        headers=["Страна", "Самолётов"],
    )


def _db_all_aeroplanes() -> None:
    rows = DBManager().get_all_aeroplanes()
    _print_db_table(
        rows,
        columns=["callsign", "origin_country", "velocity", "baro_altitude", "country"],
        headers=["Позывной", "Страна рег.", "Скорость", "Высота", "В пространстве"],
    )


def _db_avg_speed() -> None:
    avg = DBManager().get_avg_speed()
    if avg is None:
        print("Нет данных о скорости.")
    else:
        print(f"Средняя скорость: {avg:.2f} м/с")


def _db_higher_speed() -> None:
    rows = DBManager().get_aeroplanes_with_higher_speed()
    _print_db_table(
        rows,
        columns=["callsign", "origin_country", "velocity", "baro_altitude", "country"],
        headers=["Позывной", "Страна рег.", "Скорость", "Высота", "В пространстве"],
    )


def _db_keyword() -> None:
    kw = _safe_input("Введите фрагмент позывного (например, ACA): ")
    if not kw:
        print("Пустой запрос.")
        return
    rows = DBManager().get_aeroplanes_with_keyword(kw)
    _print_db_table(
        rows,
        columns=["callsign", "origin_country", "velocity", "baro_altitude", "country"],
        headers=["Позывной", "Страна рег.", "Скорость", "Высота", "В пространстве"],
    )


def _db_clear() -> None:
    """Полностью очищает таблицы БД (countries + aeroplanes)."""
    confirm = _safe_input("Удалить ВСЕ данные из БД? (y/n): ").lower()
    if confirm != "y":
        print("Отменено.")
        return
    import psycopg2
    from config import DB_CONFIG
    try:
        with psycopg2.connect(**DB_CONFIG) as conn, conn.cursor() as cur:
            # CASCADE удалит и aeroplanes, т.к. есть FK ON DELETE CASCADE
            cur.execute("TRUNCATE TABLE countries RESTART IDENTITY CASCADE;")
        print("БД очищена.")
    except Exception as e:
        print(f"Ошибка БД: {e}")


# ---------------------------------------------------------------------------
# Меню
# ---------------------------------------------------------------------------

MENU = """
╔══════════════════════════════════════════════════════╗
║        Информация о самолётах (OpenSky Network)      ║
╠══════════════════════════════════════════════════════╣
║                Файловое хранилище                    ║
║  1. Загрузить самолёты по стране                     ║
║  2. Топ-N по высоте полёта                           ║
║  3. Самолёты по стране регистрации                   ║
║  4. Топ-N по скорости                                ║
║  5. Фильтр по диапазону высот                        ║
║  6. Показать всё хранилище                           ║
║  7. Очистить хранилище                               ║
╠══════════════════════════════════════════════════════╣
║                  PostgreSQL (БД)                     ║
║  8. Заполнить БД (4 страны)                          ║
║  9. Страны и количество самолётов                    ║
║ 10. Все самолёты в БД                                ║
║ 11. Средняя скорость                                 ║
║ 12. Самолёты быстрее средней                         ║
║ 13. Поиск по позывному                               ║
║ 14. Очистить БД                                      ║
╠══════════════════════════════════════════════════════╣
║  0. Выход                                            ║
╚══════════════════════════════════════════════════════╝
"""


def user_interaction(filename: str = "aeroplanes.json") -> None:
    """Главная функция взаимодействия с пользователем через консоль."""
    storage = JSONStorage(filename)

    actions = {
        # файловое хранилище
        "1": lambda: _load_aeroplanes(storage),
        "2": lambda: _top_by_altitude(storage),
        "3": lambda: _filter_by_country(storage),
        "4": lambda: _top_by_velocity(storage),
        "5": lambda: _filter_by_altitude_range(storage),
        "6": lambda: _print_table(storage.get_all()),
        "7": lambda: _clear_storage(storage),
        # PostgreSQL
        "8":  _fill_db,
        "9":  _db_countries_stats,
        "10": _db_all_aeroplanes,
        "11": _db_avg_speed,
        "12": _db_higher_speed,
        "13": _db_keyword,
        "14": _db_clear,
    }

    while True:
        print(MENU)
        choice = _safe_input("Выберите пункт: ")

        if choice == "0":
            print("До встречи!")
            return

        action = actions.get(choice)
        if action is None:
            print("Нет такого пункта. Введите число от 0 до 14.")
            continue

        try:
            action()
        except Exception as e:
            print(f"Ошибка при выполнении пункта {choice}: {e}")

        _safe_input("\nНажмите Enter, чтобы продолжить…")


if __name__ == "__main__":
    user_interaction()