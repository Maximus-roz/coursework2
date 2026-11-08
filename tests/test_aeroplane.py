import pytest

from aeroplanes_info import Aeroplane


class TestValidation:
    """Проверка валидаторов при создании объекта."""

    def test_callsign_stripped(self):
        p = Aeroplane("  AFL123  ", "Russia", 250.0, 10000.0)
        assert p.callsign == "AFL123"

    def test_callsign_none_becomes_unknown(self):
        p = Aeroplane(None, "Russia", 250.0, 10000.0)
        assert p.callsign == "Unknown"

    def test_callsign_empty_becomes_unknown(self):
        p = Aeroplane("   ", "Russia", 250.0, 10000.0)
        assert p.callsign == "Unknown"

    def test_callsign_wrong_type_raises(self):
        with pytest.raises(TypeError):
            Aeroplane(12345, "Russia", 250.0, 10000.0)

    def test_origin_country_stripped(self):
        p = Aeroplane("AFL1", "  Russia  ", 250.0, 10000.0)
        assert p.origin_country == "Russia"

    def test_origin_country_empty_raises(self):
        with pytest.raises(ValueError):
            Aeroplane("AFL1", "   ", 250.0, 10000.0)

    def test_origin_country_none_raises(self):
        with pytest.raises(ValueError):
            Aeroplane("AFL1", None, 250.0, 10000.0)

    def test_velocity_negative_raises(self):
        with pytest.raises(ValueError):
            Aeroplane("AFL1", "Russia", -10.0, 10000.0)

    def test_velocity_none_allowed(self):
        p = Aeroplane("AFL1", "Russia", None, 10000.0)
        assert p.velocity is None

    def test_velocity_converted_to_float(self):
        p = Aeroplane("AFL1", "Russia", 250, 10000)
        assert isinstance(p.velocity, float)
        assert isinstance(p.baro_altitude, float)

    def test_velocity_wrong_type_raises(self):
        with pytest.raises(TypeError):
            Aeroplane("AFL1", "Russia", "fast", 10000.0)

    def test_altitude_negative_allowed(self):
        """При посадке высота может быть отрицательной."""
        p = Aeroplane("AFL1", "Russia", 50.0, -20.0)
        assert p.baro_altitude == -20.0

    def test_altitude_none_allowed(self):
        p = Aeroplane("AFL1", "Russia", 250.0, None)
        assert p.baro_altitude is None


class TestComparisonByVelocity:
    """Dunder-методы сравнения по скорости."""

    def test_eq_same_velocity(self):
        a = Aeroplane("A", "X", 250.0, 1000.0)
        b = Aeroplane("B", "Y", 250.0, 5000.0)
        assert a == b  # скорость одинакова, высота игнорируется

    def test_eq_diff_velocity(self):
        a = Aeroplane("A", "X", 250.0, 1000.0)
        b = Aeroplane("B", "Y", 200.0, 1000.0)
        assert a != b

    def test_eq_with_other_type_returns_not_equal(self):
        p = Aeroplane("A", "X", 250.0, 1000.0)
        assert (p == "string") is False

    def test_lt(self, plane_fast, plane_slow):
        assert plane_slow < plane_fast

    def test_le_equal(self):
        a = Aeroplane("A", "X", 250.0, 1000.0)
        b = Aeroplane("B", "Y", 250.0, 5000.0)
        assert a <= b

    def test_gt(self, plane_fast, plane_slow):
        assert plane_fast > plane_slow

    def test_ge_equal(self):
        a = Aeroplane("A", "X", 250.0, 1000.0)
        b = Aeroplane("B", "Y", 250.0, 5000.0)
        assert a >= b

    def test_compare_with_none_velocity_raises(self, plane_fast, plane_no_data):
        with pytest.raises(ValueError):
            plane_fast < plane_no_data

    def test_sort_by_velocity(self):
        planes = [
            Aeroplane("A", "X", 300.0, 1000.0),
            Aeroplane("B", "Y", 100.0, 2000.0),
            Aeroplane("C", "Z", 200.0, 3000.0),
        ]
        sorted_planes = sorted(planes)
        assert [p.velocity for p in sorted_planes] == [100.0, 200.0, 300.0]

    def test_max_returns_fastest(self):
        planes = [
            Aeroplane("A", "X", 300.0, 1000.0),
            Aeroplane("B", "Y", 400.0, 2000.0),
        ]
        assert max(planes).callsign == "B"


class TestComparisonByAltitude:
    """Методы сравнения по высоте."""

    def test_is_higher_than_true(self, plane_high, plane_fast):
        assert plane_high.is_higher_than(plane_fast)

    def test_is_higher_than_false(self, plane_fast, plane_high):
        assert not plane_fast.is_higher_than(plane_high)

    def test_is_lower_than_true(self, plane_fast, plane_high):
        assert plane_fast.is_lower_than(plane_high)

    def test_is_higher_than_wrong_type_raises(self, plane_fast):
        with pytest.raises(TypeError):
            plane_fast.is_higher_than("not a plane")

    def test_is_higher_than_none_raises(self, plane_fast, plane_no_data):
        with pytest.raises(ValueError):
            plane_fast.is_higher_than(plane_no_data)


class TestRepr:
    def test_repr_contains_all_fields(self, plane_fast):
        r = repr(plane_fast)
        assert "AFL123" in r
        assert "Russia" in r
        assert "250.0" in r
        assert "10000.0" in r
        assert r.startswith("Aeroplane(")