"""
 DEXSWAP Unit Test
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from dxsp import DexSwap
from dxsp.config import settings


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


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"


@pytest.mark.asyncio
async def test_get_swap_1(dex_client):
    result = await dex_client.get_swap(sell_token="USDT", buy_token="WBTC", quantity=1)
    assert result is not None


@pytest.mark.asyncio
async def test_get_swap_2(dex_client):
    # Mock the contract_utils.get_data method
    #dex_client.contract_utils.get_data = AsyncMock()

    # Mock the get_order_amount method
    dex_client.get_order_amount = AsyncMock(return_value="1")

    # Mock the account.get_approve method
    dex_client.account.get_approve = AsyncMock()

    # Mock the make_swap method
    dex_client.make_swap = AsyncMock()

    # Mock the account.get_sign method
    dex_client.account.get_sign = AsyncMock()

    # Mock the w3.to_hex method
    dex_client.w3.to_hex = MagicMock(return_value="mocked_order_hash")

    # Mock the w3.wait_for_transaction_receipt method
    dex_client.w3.wait_for_transaction_receipt = MagicMock(return_value={"status": 1})

    # Mock the account.get_confirmation method
    dex_client.account.get_confirmation = AsyncMock()

    # Call the get_swap method
    await dex_client.get_swap(sell_token="USDT", buy_token="WBTC", quantity=1)

    # Assertions
    # assert result == "mocked_confirmation"
    assert dex_client.contract_utils.get_data.awaited
    assert dex_client.get_order_amount.awaited
    assert dex_client.account.get_approve.awaited
    assert dex_client.make_swap.awaited
    assert dex_client.account.get_sign.awaited
    assert dex_client.w3.to_hex.called
    assert dex_client.w3.wait_for_transaction_receipt.called
    assert dex_client.account.get_confirmation.awaited


@pytest.mark.asyncio
async def test_get_token_exception(dex_client, caplog):
    await dex_client.get_quote(symbol="NOTATHING")
    assert "Quote failed" in caplog.text


@pytest.mark.asyncio
async def test_get_cg_data(dex_client):
    get_cg_data = AsyncMock()
    result = await dex_client.get_quote(symbol="LINK")
    assert result is not None
    assert isinstance(result, float)
    assert get_cg_data.awaited


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
        "to": "0x1234567890123456789012345678901234567890",
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
async def test_get_confirmation(dex_client):
    result = await dex_client.contract_utils.get_confirmation(
        "0xda56e5f1a26241a03d3f96740989e432ca41ae35b5a1b44bcb37aa2cf7772771"
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
