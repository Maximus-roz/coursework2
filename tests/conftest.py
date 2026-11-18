import sys
from pathlib import Path


from _pytest.fixtures import fixture


# чтобы тесты видели модули проекта
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.aeroplanes_info import Aeroplane


@fixture
def plane_fast():
    return Aeroplane("AFL123", "Russia", 250.0, 10000.0)


@fixture
def plane_slow():
    return Aeroplane("BAW7", "United Kingdom", 200.0, 11000.0)


@fixture
def plane_high():
    return Aeroplane("ITY1", "Italy", 230.0, 12000.0)


@fixture
def plane_no_data():
    return Aeroplane(None, "France", None, None)


@fixture
def tmp_json(tmp_path):
    """Пустой JSON-файл во временной директории."""
    return tmp_path / "test.json"