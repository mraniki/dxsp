"""
 DEXclient Unit Test
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


@pytest.fixture(name="dex_client_zero_x")
def client_zero_x_fixture(dex):
    for dx in dex.clients:
        if dx.protocol == "zerox":
            return dx


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"


@pytest.mark.asyncio
async def test_get_order_amount(dex_client):
    sell_token = AsyncMock()
    sell_token.get_token_balance.return_value = 10000
    sell_token.decimals = 6
    quantity = 50
    # Test when is_percentage is True
    result = await dex_client.get_order_amount(
        sell_token, dex_client.wallet_address, quantity
    )
    assert result == 5000.0

    # Test when is_percentage is False and balance is not zero
    result = await dex_client.get_order_amount(
        sell_token, dex_client.wallet_address, 50, False
    )
    assert result == 50

    # Test when is_percentage is False and balance is zero
    sell_token.get_token_balance.return_value = 0
    result = await dex_client.get_order_amount(
        sell_token, dex_client.wallet_address, 50, False
    )
    assert result == 0


# @pytest.mark.asyncio
# async def test_get_swap_1(dex_client):
#     result = await dex_client.get_swap(
#         sell_token="USDT",
#         buy_token="WBTC",quantity=1
#         )
#     assert result is not None


@pytest.mark.asyncio
async def test_get_swap_2(dex_client):
    dex_client.get_order_amount = AsyncMock(return_value="1")
    dex_client.account.get_approve = AsyncMock()
    dex_client.make_swap = AsyncMock()
    dex_client.account.get_sign = AsyncMock()
    dex_client.w3.to_hex = MagicMock(
        return_value="0xea5a0fd0a15f68ef2f4b38661d445aa14de06a88844adc236bb071c46734fd09"
    )
    dex_client.w3.wait_for_transaction_receipt = (
        dex_client.w3.eth.wait_for_transaction_receipt(
            "0xea5a0fd0a15f68ef2f4b38661d445aa14de06a88844adc236bb071c46734fd09"
        )
    )
    dex_client.account.get_confirmation = AsyncMock()
    result = await dex_client.get_swap(sell_token="USDT", buy_token="WBTC", quantity=1)

    assert result is not None
    assert dex_client.account.get_confirmation.awaited


@pytest.mark.asyncio
async def test_get_trading_asset_balance(dex_client):
    dex_client.account.get_trading_asset_balance = AsyncMock()
    result = await dex_client.get_trading_asset_balance()
    assert result is not None
    assert dex_client.account.get_trading_asset_balance.awaited


@pytest.mark.asyncio
async def test_get_account_open_positions(dex_client):
    dex_client.account.get_account_open_positions = AsyncMock()
    result = await dex_client.get_account_open_positions()
    assert result is not None
    assert dex_client.account.get_account_open_positions.awaited


@pytest.mark.asyncio
async def test_get_account_margin(dex_client):
    dex_client.account.get_account_margin = AsyncMock()
    result = await dex_client.get_account_margin()
    assert result is not None
    assert dex_client.account.get_account_margin.awaited


@pytest.mark.asyncio
async def test_get_account_pnl(dex_client):
    dex_client.account.get_account_pnl = AsyncMock()
    result = await dex_client.get_account_pnl()
    assert result is not None
    assert dex_client.account.get_account_pnl.awaited


@pytest.mark.asyncio
async def test_get_cg_data(dex_client):
    result = await dex_client.get_quote(sell_symbol="LINK")
    assert result is not None
    assert isinstance(result, float)


@pytest.mark.asyncio
async def test_get_token_exception(dex_client, caplog):
    await dex_client.get_quote(sell_symbol="NOTATHING")
    assert "Quote failed" in caplog.text


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


# @pytest.mark.asyncio
# async def test_get_gas_price(dex_client):
#     result = await dex_client.account.get_gas_price()
#     print(f"gas_price: {result}")
#     assert result is not None


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


# @pytest.mark.asyncio
# async def test_get_quote_zero_x(dex_client_zero_x):

#     result = await dex_client_zero_x.get_quote(
#         buy_address="0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",  # USDT
#         sell_address="0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6",  # WBTC
#         amount=1,
#     )

#     # Assert the result
#     assert result is not None
#     assert result > 0
