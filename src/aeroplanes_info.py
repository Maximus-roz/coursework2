class Aeroplane:
    """Класс для хранения и валидации информации о самолёте."""

    def __init__(self, callsign, origin_country, velocity, baro_altitude):
        self.callsign = self._validate_callsign(callsign)
        self.origin_country = self._validate_origin_country(origin_country)
        self.velocity = self._validate_velocity(velocity)
        self.baro_altitude = self._validate_altitude(baro_altitude)

    @staticmethod
    def _validate_callsign(value):
        """Позывной: строка, может быть None или содержать пробелы (обрезаем)."""
        if value is None:
            return "Unknown"
        if not isinstance(value, str):
            raise TypeError("Позывной должен быть строкой или None")
        stripped = value.strip()
        return stripped if stripped else "Unknown"

    @staticmethod
    def _validate_origin_country(value):
        """Страна регистрации: непустая строка."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Страна регистрации должна быть непустой строкой")
        return value.strip()

    @staticmethod
    def _validate_velocity(value):
        """Скорость: число >= 0 или None (если данных нет)."""
        if value is None:
            return None
        if not isinstance(value, (int, float)):
            raise TypeError("Скорость должна быть числом или None")
        if value < 0:
            raise ValueError("Скорость не может быть отрицательной")
        return float(value)

    @staticmethod
    def _validate_altitude(value):
        """Высота: число (может быть отрицательной при посадке) или None."""
        if value is None:
            return None
        if not isinstance(value, (int, float)):
            raise TypeError("Высота должна быть числом или None")
        return float(value)

 # --- Методы сравнения ---

    # Сравнение по скорости — через операторы
    def __eq__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.velocity == other.velocity

    def __lt__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        if self.velocity is None or other.velocity is None:
            raise ValueError("Нет данных о скорости")
        return self.velocity < other.velocity

    def __le__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        if self.velocity is None or other.velocity is None:
            raise ValueError("Нет данных о скорости")
        return self.velocity <= other.velocity

    def __gt__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        if self.velocity is None or other.velocity is None:
            raise ValueError("Нет данных о скорости")
        return self.velocity > other.velocity

    def __ge__(self, other):
        if not isinstance(other, Aeroplane):
            return NotImplemented
        if self.velocity is None or other.velocity is None:
            raise ValueError("Нет данных о скорости")
        return self.velocity >= other.velocity

    # Сравнение по высоте — отдельные методы, т.к. операторы уже заняты скоростью
    def is_higher_than(self, other):
        if not isinstance(other, Aeroplane):
            raise TypeError("Ожидался объект Aeroplane")
        if self.baro_altitude is None or other.baro_altitude is None:
            raise ValueError("Нет данных о высоте")
        return self.baro_altitude > other.baro_altitude

    def is_lower_than(self, other):
        if not isinstance(other, Aeroplane):
            raise TypeError("Ожидался объект Aeroplane")
        if self.baro_altitude is None or other.baro_altitude is None:
            raise ValueError("Нет данных о высоте")
        return self.baro_altitude < other.baro_altitude

    def __repr__(self):
        return (f"Aeroplane(callsign={self.callsign!r}, "
                f"country={self.origin_country!r}, "
                f"velocity={self.velocity}, "
                f"altitude={self.baro_altitude})")