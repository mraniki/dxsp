import pytest
from unittest.mock import patch, MagicMock
from dxsp import DexSwap

@pytest.fixture
def my_dex():
    return DexSwap()

@pytest.mark.asyncio
async def test__get(my_class):
    url = "https://example.com"
    params = {"param1": "value1", "param2": "value2"}
    headers = {"header1": "value1", "header2": "value2"}

    with patch("dxsp.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        result = await DexSwap._get(url, params=params, headers=headers)

        mock_get.assert_called_once_with(url, params=params, headers=headers, timeout=10)
        assert result == {"key": "value"}