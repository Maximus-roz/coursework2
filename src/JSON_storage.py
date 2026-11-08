import json
import os
from pathlib import Path

from Abstract_file_storage import AbstractFileStorage


class JSONStorage(AbstractFileStorage):
    """Хранилище самолётов в JSON-файле.

    Структура файла — список словарей:
        [{"callsign": "...", "origin_country": "...", ...}, ...]
    """

    def __init__(self, filename: str = "aeroplanes.json") -> None:
        self.filename = Path(filename)

    # --- Вспомогательные методы ---

    def _read(self) -> list:
        """Читает файл. Если файла нет — возвращает пустой список."""
        if not self.filename.exists():
            return []
        with open(self.filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return []
        return data if isinstance(data, list) else []

    def _write(self, data: list) -> None:
        """Перезаписывает файл."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _to_dict(aeroplane) -> dict:
        return {
            "callsign": aeroplane.callsign,
            "origin_country": aeroplane.origin_country,
            "velocity": aeroplane.velocity,
            "baro_altitude": aeroplane.baro_altitude,
        }

    @staticmethod
    def _matches(record: dict, criteria: dict) -> bool:
        """Проверяет, удовлетворяет ли запись критериям.

        Поддерживает:
          - точное совпадение: origin_country="Russia"
          - min_<attr> / max_<attr>: min_velocity=200.0
          - None как «любое значение» (критерий игнорируется)
        """
        for key, expected in criteria.items():
            if expected is None:
                continue
            if key.startswith("min_"):
                attr = key[4:]
                if record.get(attr) is None or record[attr] < expected:
                    return False
            elif key.startswith("max_"):
                attr = key[4:]
                if record.get(attr) is None or record[attr] > expected:
                    return False
            else:
                if record.get(key) != expected:
                    return False
        return True

    # --- Реализация абстрактных методов ---

    def add_aeroplane(self, aeroplane) -> None:
        data = self._read()
        data.append(self._to_dict(aeroplane))
        self._write(data)

    def get_aeroplanes(self, **criteria) -> list:
        data = self._read()
        return [rec for rec in data if self._matches(rec, criteria)]

    def delete_aeroplanes(self, **criteria) -> int:
        data = self._read()
        kept = [rec for rec in data if not self._matches(rec, criteria)]
        removed = len(data) - len(kept)
        if removed:
            self._write(kept)
        return removed

    # --- Переопределение заглушек там, где для файлов это осмысленно ---

    def get_all(self) -> list:
        return self._read()

    def clear(self) -> None:
        self._write([])