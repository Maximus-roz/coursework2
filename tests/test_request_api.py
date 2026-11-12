
from unittest.mock import patch, MagicMock

import pytest

from request_api import APIAdapter, AbstractAPIAdapter


def _mock_response(json_data):
    m = MagicMock()
    m.json.return_value = json_data
    return m


class TestAbstractClass:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            AbstractAPIAdapter()

    def test_adapter_is_subclass(self):
        assert issubclass(APIAdapter, AbstractAPIAdapter)


class TestGetGeoCoordinates:
    @patch("request_api.get")
    def test_returns_boundingbox(self, mock_get):
        mock_get.return_value = _mock_response([
            {"boundingbox": ["35.0", "47.0", "6.0", "18.0"]}
        ])
        adapter = APIAdapter()
        result = adapter.get_geo_coordinates("italia")
        assert result == ["35.0", "47.0", "6.0", "18.0"]

    @patch("request_api.get")
    def test_passes_user_agent_header(self, mock_get):
        mock_get.return_value = _mock_response([
            {"boundingbox": ["0", "1", "0", "1"]}
        ])
        adapter = APIAdapter()
        adapter.get_geo_coordinates("italia")
        _, kwargs = mock_get.call_args
        assert "User-Agent" in kwargs["headers"]

    @patch("request_api.get")
    def test_country_not_found_raises(self, mock_get):
        mock_get.return_value = _mock_response([])
        adapter = APIAdapter()
        with pytest.raises(ValueError, match="не найдена"):
            adapter.get_geo_coordinates("Atlantis")


class TestGetAeroplanes:
    @patch("request_api.get")
    def test_returns_states(self, mock_get):
        # первый вызов — nominatim, второй — opensky
        mock_get.side_effect = [
            _mock_response([{"boundingbox": ["35.0", "47.0", "6.0", "18.0"]}]),
            _mock_response({"states": [["abc", "AFL1", "Russia"]]}),
        ]
        adapter = APIAdapter()
        result = adapter.get_aeroplanes("italia")
        assert result["states"][0][1] == "AFL1"

    @patch("request_api.get")
    def test_passes_boundingbox_as_opensky_params(self, mock_get):
        mock_get.side_effect = [
            _mock_response([{"boundingbox": ["35.0", "47.0", "6.0", "18.0"]}]),
            _mock_response({"states": []}),
        ]
        adapter = APIAdapter()
        adapter.get_aeroplanes("italia")

        # второй вызов — к opensky, проверяем параметры
        _, kwargs = mock_get.call_args
        params = kwargs["params"]
        assert params == {
            "lamin": "35.0",
            "lamax": "47.0",
            "lomin": "6.0",
            "lomax": "18.0",
        }