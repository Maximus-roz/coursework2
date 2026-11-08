import json

import pytest

from aeroplanes_info import Aeroplane
from JSON_storage import JSONStorage


@pytest.fixture
def storage(tmp_json):
    return JSONStorage(str(tmp_json))


class TestAdd:
    def test_add_creates_file(self, storage, tmp_json, plane_fast):
        assert not tmp_json.exists()
        storage.add_aeroplane(plane_fast)
        assert tmp_json.exists()

    def test_add_persists_data(self, storage, tmp_json, plane_fast):
        storage.add_aeroplane(plane_fast)
        data = json.loads(tmp_json.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["callsign"] == "AFL123"
        assert data[0]["origin_country"] == "Russia"
        assert data[0]["velocity"] == 250.0
        assert data[0]["baro_altitude"] == 10000.0

    def test_add_multiple(self, storage, tmp_json, plane_fast, plane_slow):
        storage.add_aeroplane(plane_fast)
        storage.add_aeroplane(plane_slow)
        data = json.loads(tmp_json.read_text(encoding="utf-8"))
        assert len(data) == 2

    def test_add_none_values(self, storage, tmp_json, plane_no_data):
        storage.add_aeroplane(plane_no_data)
        data = json.loads(tmp_json.read_text(encoding="utf-8"))
        assert data[0]["velocity"] is None
        assert data[0]["baro_altitude"] is None


class TestGet:
    def test_get_all_empty(self, storage):
        assert storage.get_all() == []

    def test_get_all_after_add(self, storage, plane_fast, plane_slow):
        storage.add_aeroplane(plane_fast)
        storage.add_aeroplane(plane_slow)
        assert len(storage.get_all()) == 2

    def test_get_by_country_exact(self, storage, plane_fast, plane_slow):
        storage.add_aeroplane(plane_fast)
        storage.add_aeroplane(plane_slow)
        result = storage.get_aeroplanes(origin_country="Russia")
        assert len(result) == 1
        assert result[0]["callsign"] == "AFL123"

    def test_get_by_country_no_match(self, storage, plane_fast):
        storage.add_aeroplane(plane_fast)
        assert storage.get_aeroplanes(origin_country="Mars") == []

    def test_get_by_min_velocity(self, storage, plane_fast, plane_slow):
        storage.add_aeroplane(plane_fast)    # 250
        storage.add_aeroplane(plane_slow)    # 200
        result = storage.get_aeroplanes(min_velocity=220.0)
        assert len(result) == 1
        assert result[0]["callsign"] == "AFL123"

    def test_get_by_max_velocity(self, storage, plane_fast, plane_slow):
        storage.add_aeroplane(plane_fast)    # 250
        storage.add_aeroplane(plane_slow)    # 200
        result = storage.get_aeroplanes(max_velocity=220.0)
        assert len(result) == 1
        assert result[0]["callsign"] == "BAW7"

    def test_get_by_altitude_range(self, storage, plane_fast, plane_high):
        storage.add_aeroplane(plane_fast)    # 10000
        storage.add_aeroplane(plane_high)    # 12000
        result = storage.get_aeroplanes(
            min_baro_altitude=11000.0,
            max_baro_altitude=13000.0,
        )
        assert len(result) == 1
        assert result[0]["callsign"] == "ITY1"

    def test_get_ignores_none_criteria(self, storage, plane_fast):
        storage.add_aeroplane(plane_fast)
        # None = критерий не задан
        assert len(storage.get_aeroplanes(min_velocity=None)) == 1

    def test_get_min_velocity_skips_null(self, storage, plane_no_data):
        """Записи без скорости не должны попадать в min_-фильтр."""
        storage.add_aeroplane(plane_no_data)
        assert storage.get_aeroplanes(min_velocity=0.0) == []


class TestDelete:
    def test_delete_by_country(self, storage, plane_fast, plane_slow):
        storage.add_aeroplane(plane_fast)
        storage.add_aeroplane(plane_slow)
        removed = storage.delete_aeroplanes(origin_country="Russia")
        assert removed == 1
        assert len(storage.get_all()) == 1

    def test_delete_nothing_returns_zero(self, storage, plane_fast):
        storage.add_aeroplane(plane_fast)
        assert storage.delete_aeroplanes(origin_country="Mars") == 0
        assert len(storage.get_all()) == 1

    def test_delete_all_with_empty_criteria(self, storage, plane_fast, plane_slow):
        storage.add_aeroplane(plane_fast)
        storage.add_aeroplane(plane_slow)
        removed = storage.delete_aeroplanes()
        assert removed == 2
        assert storage.get_all() == []

    def test_delete_does_not_touch_file_when_nothing_removed(
        self, storage, tmp_json, plane_fast
    ):
        storage.add_aeroplane(plane_fast)
        mtime_before = tmp_json.stat().st_mtime_ns
        storage.delete_aeroplanes(origin_country="Mars")
        assert tmp_json.stat().st_mtime_ns == mtime_before


class TestClear:
    def test_clear_empties_file(self, storage, tmp_json, plane_fast):
        storage.add_aeroplane(plane_fast)
        storage.clear()
        assert storage.get_all() == []
        assert json.loads(tmp_json.read_text(encoding="utf-8")) == []


class TestRobustness:
    def test_read_missing_file_returns_empty(self, storage):
        assert storage.get_all() == []

    def test_read_broken_json_returns_empty(self, storage, tmp_json):
        tmp_json.write_text("{ broken json", encoding="utf-8")
        assert storage.get_all() == []

    def test_read_non_list_json_returns_empty(self, storage, tmp_json):
        tmp_json.write_text('{"not": "a list"}', encoding="utf-8")
        assert storage.get_all() == []


class TestAbstractContract:
    def test_get_all_and_clear_implemented(self, storage):
        """JSONStorage переопределяет заглушки — они не должны бросать."""
        storage.get_all()
        storage.clear()

    def test_update_not_implemented(self, storage, plane_fast):
        """update_aeroplane остаётся заглушкой в JSONStorage."""
        with pytest.raises(NotImplementedError):
            storage.update_aeroplane(plane_fast)