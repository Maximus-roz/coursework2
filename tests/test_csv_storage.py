import pytest

from aeroplanes_info import Aeroplane
from CSV_storage import CSVStorage


@pytest.fixture
def storage(tmp_path):
    return CSVStorage(str(tmp_path / "test.csv"))


class TestCSV:
    def test_add_and_get_all(self, storage, plane_fast):
        storage.add_aeroplane(plane_fast)
        result = storage.get_all()
        assert len(result) == 1
        # CSV хранит строки, читаем обратно уже с приведением типов
        assert result[0]["callsign"] == "AFL123"
        assert result[0]["velocity"] == 250.0

    def test_none_roundtrip(self, storage, plane_no_data):
        storage.add_aeroplane(plane_no_data)
        result = storage.get_all()
        assert result[0]["velocity"] is None
        assert result[0]["baro_altitude"] is None

    def test_filter_by_country(self, storage, plane_fast, plane_slow):
        storage.add_aeroplane(plane_fast)
        storage.add_aeroplane(plane_slow)
        result = storage.get_aeroplanes(origin_country="Russia")
        assert len(result) == 1

    def test_min_velocity_works(self, storage, plane_fast, plane_slow):
        storage.add_aeroplane(plane_fast)
        storage.add_aeroplane(plane_slow)
        result = storage.get_aeroplanes(min_velocity=220.0)
        assert len(result) == 1
        assert result[0]["callsign"] == "AFL123"

    def test_delete_by_country(self, storage, plane_fast, plane_slow):
        storage.add_aeroplane(plane_fast)
        storage.add_aeroplane(plane_slow)
        removed = storage.delete_aeroplanes(origin_country="Russia")
        assert removed == 1
        assert len(storage.get_all()) == 1