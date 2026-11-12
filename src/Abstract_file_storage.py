from abc import ABC, abstractmethod


class AbstractFileStorage(ABC):
    """Абстрактный класс хранилища информации о самолётах.

    Обязывает наследников реализовать добавление, чтение по критериям
    и удаление. Формат хранения (JSON, CSV, TXT, БД) определяет наследник.
    """

    @abstractmethod
    def add_aeroplane(self, aeroplane) -> None:
        """Добавить один самолёт в хранилище."""
        pass

    @abstractmethod
    def get_aeroplanes(self, **criteria) -> list:
        """Получить список самолётов, удовлетворяющих критериям.

        criteria — произвольные пары «атрибут=значение», например:
            get_aeroplanes(origin_country="Russia")
            get_aeroplanes(min_velocity=200.0)
        """
        pass

    @abstractmethod
    def delete_aeroplanes(self, **criteria) -> int:
        """Удалить самолёты, удовлетворяющие критериям.

        Возвращает количество удалённых записей.
        """
        pass

    # --- Методы-заглушки для будущей интеграции с БД ---

    def get_all(self) -> list:
        """Получить все записи. Для файлов реализуется через get_aeroplanes()."""
        raise NotImplementedError(
            "Метод get_all будет реализован в коннекторе БД"
        )

    def clear(self) -> None:
        """Полностью очистить хранилище. Для БД — TRUNCATE TABLE."""
        raise NotImplementedError(
            "Метод clear будет реализован в коннекторе БД"
        )

    def update_aeroplane(self, aeroplane) -> None:
        """Обновить запись. Для файлов удобнее delete + add."""
        raise NotImplementedError(
            "Метод update_aeroplane будет реализован в коннекторе БД"
        )