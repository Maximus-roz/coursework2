from request_api import APIAdapter
from aeroplanes_info import Aeroplane
from JSON_storage import JSONStorage


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


def _load_aeroplanes(storage: JSONStorage) -> None:
    """Запрашивает страну у пользователя и сохраняет самолёты в хранилище."""
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
        except (TypeError, ValueError) as e:
            # одна битая запись не должна ронять весь импорт
            continue
        storage.add_aeroplane(plane)
        added += 1

    print(f"Сохранено самолётов: {added} из {len(states)}.")


def _print_table(records: list, limit: int = None) -> None:
    """Печатает список записей (dict) в виде таблицы."""
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


def _top_by_altitude(storage: JSONStorage) -> None:
    n = _ask_int("Сколько самолётов показать (N)? [по умолчанию 10]: ")
    records = storage.get_all()
    # сортируем по высоте по убыванию, отбрасываем записи без высоты
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


MENU = """
╔══════════════════════════════════════════════════════╗
║        Информация о самолётах (OpenSky Network)      ║
╠══════════════════════════════════════════════════════╣
║  1. Загрузить самолёты по стране                     ║
║  2. Топ-N по высоте полёта                           ║
║  3. Самолёты по стране регистрации                   ║
║  4. Топ-N по скорости                                ║
║  5. Фильтр по диапазону высот                        ║
║  6. Показать всё хранилище                           ║
║  7. Очистить хранилище                               ║
║  0. Выход                                            ║
╚══════════════════════════════════════════════════════╝
"""


def user_interaction(filename: str = "aeroplanes.json") -> None:
    """Главная функция взаимодействия с пользователем через консоль."""
    storage = JSONStorage(filename)

    actions = {
        "1": lambda: _load_aeroplanes(storage),
        "2": lambda: _top_by_altitude(storage),
        "3": lambda: _filter_by_country(storage),
        "4": lambda: _top_by_velocity(storage),
        "5": lambda: _filter_by_altitude_range(storage),
        "6": lambda: _print_table(storage.get_all()),
        "7": lambda: _clear_storage(storage),
    }

    while True:
        print(MENU)
        choice = _safe_input("Выберите пункт: ")

        if choice == "0":
            print("До встречи!")
            return

        action = actions.get(choice)
        if action is None:
            print("Нет такого пункта. Введите число от 0 до 7.")
            continue

        try:
            action()
        except Exception as e:
            # последняя линия обороны: пункт меню не должен ронять программу
            print(f"Ошибка при выполнении пункта {choice}: {e}")

        _safe_input("\nНажмите Enter, чтобы продолжить…")


if __name__ == "__main__":
    user_interaction()