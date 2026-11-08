"""Точка входа программы.

Запуск:
    python main.py
Опционально с указанием файла хранилища:
    python main.py my_data.json
"""

import sys

from user_interaction import user_interaction


def main() -> None:
    filename = sys.argv[1] if len(sys.argv) > 1 else "aeroplanes.json"
    print(f"Хранилище: {filename}")
    user_interaction(filename)


if __name__ == "__main__":
    main()