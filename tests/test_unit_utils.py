"""
 DEXclient Unit Test
"""

import pytest

from dxsp import DexSwap
from dxsp.config import settings
from dxsp.utils.utils import fetch_url


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="dxsp")


@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


@pytest.fixture(name="dex_client")
def client_fixture(dex):
    for dx in dex.clients:
        if dx.protocol == "uniswap":
            return dx


### UTILS CONTRACT
# @pytest.mark.asyncio
# async def test_get_cg_data(dex_client):
#     result = await dex_client.get_quote(sell_symbol="LINK")
#     assert result is not None
#     assert isinstance(result, float)


# @pytest.mark.asyncio
# async def test_get_token_exception(dex_client, caplog):
#     await dex_client.get_quote(sell_symbol="NOTATHING")
#     assert "Quote failed" in caplog.text


@pytest.mark.asyncio
async def test_get_confirmation(dex_client):
    result = await dex_client.contract_utils.get_confirmation(
        "0xea5a0fd0a15f68ef2f4b38661d445aa14de06a88844adc236bb071c46734fd09"
    )
    print(result)
    assert result is not None
    assert result["timestamp"] is not None
    assert result["fee"] is not None
    assert result["confirmation"] is not None
    assert "➕" in result["confirmation"]
    assert "⛽" in result["confirmation"]
    assert "🗓️" in result["confirmation"]
    assert "ℹ️" in result["confirmation"]


### UTILS ACCOUNT


@pytest.mark.asyncio
async def test_get_approve(dex_client):
    symbol = "UNI"
    approve_receipt = None
    try:
        approve_receipt = await dex_client.account.get_approve(symbol)
        print(approve_receipt)
    except Exception as e:
        print(f"Error getting approve receipt: {e}")
    assert approve_receipt is None


@pytest.mark.asyncio
async def test_get_gas(dex_client):
    """get_gas Testing"""
    mock_tx = {
        "to": "0x5f65f7b609678448494De4C87521CdF6cEf1e932",
        "value": "1000000000000000000",
    }
    result = await dex_client.account.get_gas(mock_tx)
    print(result)
    assert result is not None


@pytest.mark.asyncio
async def test_get_gas_price(dex_client):
    result = await dex_client.account.get_gas_price()
    print(f"gas_price: {result}")
    assert result is not None


@pytest.mark.asyncio
async def test_fetch_url_error():
    url = ""
    response = await fetch_url(url)
    assert response is None


@pytest.mark.asyncio
async def test_fetch_url_large_response(caplog):
    url = "https://github.com/json-iterator/test-data/raw/master/large-file.json"
    response = await fetch_url(url)
    assert response is None
    assert "Response content is too large to process." in caplog.text
