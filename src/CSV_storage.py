import csv
from pathlib import Path

from Abstract_file_storage import AbstractFileStorage
from JSON_storage import JSONStorage


class CSVStorage(AbstractFileStorage):
    """Хранилище самолётов в CSV-файле."""

    FIELDS = ["callsign", "origin_country", "velocity", "baro_altitude"]

    def __init__(self, filename: str = "aeroplanes.csv") -> None:
        self.filename = Path(filename)

    def _read(self) -> list:
        if not self.filename.exists():
            return []
        with open(self.filename, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                # приводим типы обратно: CSV хранит всё строками
                row["velocity"] = float(row["velocity"]) if row["velocity"] else None
                row["baro_altitude"] = float(row["baro_altitude"]) if row["baro_altitude"] else None
                rows.append(row)
            return rows

    def _write(self, data: list) -> None:
        with open(self.filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDS)
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def _to_dict(aeroplane) -> dict:
        return {
            "callsign": aeroplane.callsign,
            "origin_country": aeroplane.origin_country,
            "velocity": "" if aeroplane.velocity is None else aeroplane.velocity,
            "baro_altitude": "" if aeroplane.baro_altitude is None else aeroplane.baro_altitude,
        }

    def add_aeroplane(self, aeroplane) -> None:
        data = self._read()
        data.append(self._to_dict(aeroplane))
        self._write(data)

    def get_aeroplanes(self, **criteria) -> list:
        data = self._read()
        return [rec for rec in data if JSONStorage._matches(rec, criteria)]

    def delete_aeroplanes(self, **criteria) -> int:
        data = self._read()
        kept = [rec for rec in data if not JSONStorage._matches(rec, criteria)]
        removed = len(data) - len(kept)
        if removed:
            self._write(kept)
        return removed