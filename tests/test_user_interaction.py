import pytest

from aeroplanes_info import Aeroplane
from JSON_storage import JSONStorage
import user_interaction as ui


@pytest.fixture
def storage(tmp_path):
    return JSONStorage(str(tmp_path / "test.json"))


class TestLoadAeroplanes:
    def test_load_saves_planes(self, storage, monkeypatch):
        fake_response = {
            "states": [
                ["abc", "AFL1", "Russia", None, None, None, None, 10000.0, None, 250.0],
                ["def", "BAW7", "UK", None, None, None, None, 11000.0, None, 200.0],
            ]
        }
        monkeypatch.setattr(ui, "APIAdapter", lambda: type(
            "FakeAPI", (), {"get_aeroplanes": lambda self, c: fake_response}
        )())
        monkeypatch.setattr("builtins.input", lambda prompt="": "italia")

        ui._load_aeroplanes(storage)
        assert len(storage.get_all()) == 2

    def test_load_skips_short_states(self, storage, monkeypatch):
        fake_response = {"states": [["abc", "AFL1"], ["def"]]}
        monkeypatch.setattr(ui, "APIAdapter", lambda: type(
            "FakeAPI", (), {"get_aeroplanes": lambda self, c: fake_response}
        )())
        monkeypatch.setattr("builtins.input", lambda prompt="": "italia")

        ui._load_aeroplanes(storage)
        assert storage.get_all() == []

    def test_load_empty_country_aborts(self, storage, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        ui._load_aeroplanes(storage)
        assert "не может быть пустым" in capsys.readouterr().out


class TestTopByAltitude:
    def test_returns_sorted_desc(self, storage, monkeypatch, capsys):
        storage.add_aeroplane(Aeroplane("A", "X", 100.0, 5000.0))
        storage.add_aeroplane(Aeroplane("B", "Y", 100.0, 12000.0))
        storage.add_aeroplane(Aeroplane("C", "Z", 100.0, 8000.0))

        # N=2
        monkeypatch.setattr("builtins.input", lambda prompt="": "2")
        ui._top_by_altitude(storage)
        out = capsys.readouterr().out
        # B (12000) должен быть раньше C (8000)
        assert out.index("B") < out.index("C")
        # A (5000) не должен попасть в топ-2
        assert "Всего: 2" in out

    def test_skips_none_altitude(self, storage, monkeypatch, capsys):
        storage.add_aeroplane(Aeroplane("A", "X", 100.0, None))
        storage.add_aeroplane(Aeroplane("B", "Y", 100.0, 5000.0))
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        ui._top_by_altitude(storage)
        out = capsys.readouterr().out
        assert "Всего: 1" in out


class TestFilterByCountry:
    def test_filters(self, storage, monkeypatch, capsys):
        storage.add_aeroplane(Aeroplane("A", "Russia", 100.0, 5000.0))
        storage.add_aeroplane(Aeroplane("B", "Italy", 100.0, 5000.0))
        monkeypatch.setattr("builtins.input", lambda prompt="": "Russia")
        ui._filter_by_country(storage)
        out = capsys.readouterr().out
        assert "A" in out
        assert "B" not in out


class TestFilterByAltitudeRange:
    def test_range(self, storage, monkeypatch, capsys):
        storage.add_aeroplane(Aeroplane("A", "X", 100.0, 5000.0))
        storage.add_aeroplane(Aeroplane("B", "Y", 100.0, 8000.0))
        storage.add_aeroplane(Aeroplane("C", "Z", 100.0, 12000.0))

        answers = iter(["6000", "10000"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))

        ui._filter_by_altitude_range(storage)
        out = capsys.readouterr().out
        assert "B" in out
        assert "A" not in out
        assert "C" not in out


class TestClearStorage:
    def test_clear_on_confirm(self, storage, monkeypatch):
        storage.add_aeroplane(Aeroplane("A", "X", 100.0, 5000.0))
        monkeypatch.setattr("builtins.input", lambda prompt="": "y")
        ui._clear_storage(storage)
        assert storage.get_all() == []

    def test_no_clear_on_cancel(self, storage, monkeypatch):
        storage.add_aeroplane(Aeroplane("A", "X", 100.0, 5000.0))
        monkeypatch.setattr("builtins.input", lambda prompt="": "n")
        ui._clear_storage(storage)
        assert len(storage.get_all()) == 1


class TestUserInteractionLoop:
    def test_exit_zero(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda prompt="": "0")
        ui.user_interaction(str(tmp_path / "t.json"))
        assert "До встречи" in capsys.readouterr().out

    def test_unknown_choice_then_exit(self, tmp_path, monkeypatch, capsys):
        answers = iter(["99", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
        ui.user_interaction(str(tmp_path / "t.json"))
        assert "Нет такого пункта" in capsys.readouterr().out

    def test_show_all(self, tmp_path, monkeypatch, capsys):
        storage = JSONStorage(str(tmp_path / "t.json"))
        storage.add_aeroplane(Aeroplane("A", "X", 100.0, 5000.0))

        answers = iter(["6", "", "0"])  # показать всё, Enter, выход
        monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
        ui.user_interaction(str(tmp_path / "t.json"))
        assert "A" in capsys.readouterr().out


class TestHelpers:
    def test_safe_input_strips(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "  hi  ")
        assert ui._safe_input("x") == "hi"

    def test_safe_input_ctrl_c(self, monkeypatch):
        def raise_interrupt(prompt=""):
            raise KeyboardInterrupt()
        monkeypatch.setattr("builtins.input", raise_interrupt)
        with pytest.raises(SystemExit):
            ui._safe_input("x")

    def test_ask_int_default(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        assert ui._ask_int("x", default=7) == 7

    def test_ask_int_retries_on_invalid(self, monkeypatch):
        answers = iter(["abc", "-5", "3"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
        assert ui._ask_int("x") == 3

    def test_ask_float_none_on_empty(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        assert ui._ask_float_or_none("x") is None

    def test_ask_float_invalid_returns_none(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda prompt="": "abc")
        assert ui._ask_float_or_none("x") is None
        assert "не число" in capsys.readouterr().out