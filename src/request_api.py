from abc import ABC, abstractmethod
from requests import get


class AbstractAPIAdapter(ABC):
    """Абстрактный класс для работы с API сервисов."""

    @abstractmethod
    def get_geo_coordinates(self, country: str) -> list:
        """Получение географических координат (boundingbox) страны."""
        pass

    @abstractmethod
    def get_aeroplanes(self, country: str) -> dict:
        """Получение информации о самолётах в воздушном пространстве страны."""
        pass


class APIAdapter(AbstractAPIAdapter):
    """Класс для работы с nominatim.openstreetmap.org и opensky-network.org."""

    def __init__(self) -> None:
        self.openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
        self.opensky_url = 'https://opensky-network.org/api/states/all?'
        self.aeroplanes = None

    def get_geo_coordinates(self, country: str) -> list:
        """Возвращает boundingbox страны (список из 4 координат)."""
        # Headers с user-agent — обязательный параметр при запросе к nominatim.
        headers_nominatim = {
            'User-Agent': 'test-app/1.0',
        }

        params_nominatim = {
            'country': country,
            'format': 'json',
            'limit': 1,
        }

        response = get(
            url=self.openstreetmap_url,
            params=params_nominatim,
            headers=headers_nominatim
        )

        data = response.json()

        if not data:
            raise ValueError(f'Страна "{country}" не найдена.')

        geo_coordinates = data[0].get('boundingbox')
        return geo_coordinates

    def get_aeroplanes(self, country: str) -> dict:
        """Возвращает информацию о самолётах над страной."""
        geo_coordinates = self.get_geo_coordinates(country)
        print(f'Bounding box для "{country}": {geo_coordinates}')

        # Параметры для фильтрации самолётов по координатам.
        # ВАЖНО: nominatim возвращает boundingbox в порядке:
        # [южная широта, северная широта, западная долгота, восточная долгота]
        params = {
            'lamin': geo_coordinates[0],
            'lamax': geo_coordinates[1],
            'lomin': geo_coordinates[2],
            'lomax': geo_coordinates[3],
        }

        response = get(url=self.opensky_url, params=params)

        self.aeroplanes = response.json()
        return self.aeroplanes


if __name__ == '__main__':
    api = APIAdapter()
    result = api.get_aeroplanes('italia')
    print(result)