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


# @pytest.fixture(name="dex_client")
# def client_fixture(dex):
#     for dx in dex.clients:
#         if dx.protocol == "uniswap":
#             return dx


@pytest.fixture(name="dex_client")
def client_fixture(dex):
    for dx in dex.clients:
        if dx.name == "eth":
            return dx


@pytest.mark.asyncio
async def test_resolve_address(dex_client):
    result = await dex_client.resolve_token(
        address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    )
    assert result.symbol == "WBTC"


@pytest.mark.asyncio
async def test_resolve_symbol(dex_client):
    result = await dex_client.resolve_token(symbol="LINK")
    assert result.address == "0x514910771AF9Ca656af840dff83E8264EcF986CA"


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


@pytest.mark.asyncio
async def test_get_swap(dex_client):
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


# @pytest.mark.asyncio
# async def test_get_swap_1(dex_client):
#     result = await dex_client.get_swap(
#         sell_token="USDT",
#         buy_token="WBTC",quantity=1
#         )
#     assert result is not None


@pytest.mark.asyncio
async def test_get_trading_asset_balance(dex_client):
    dex_client.account.get_trading_asset_balance = AsyncMock()
    result = await dex_client.get_trading_asset_balance()
    assert result is not None
    assert dex_client.account.get_trading_asset_balance.awaited


# @pytest.mark.asyncio
# async def test_get_account_open_positions(dex_client):
#     dex_client.account.get_account_open_positions = AsyncMock()
#     result = await dex_client.get_account_open_positions()
#     assert result is not None
#     assert dex_client.account.get_account_open_positions.awaited


# @pytest.mark.asyncio
# async def test_get_account_margin(dex_client):
#     dex_client.account.get_account_margin = AsyncMock()
#     result = await dex_client.get_account_margin()
#     assert result is not None
#     assert dex_client.account.get_account_margin.awaited


# @pytest.mark.asyncio
# async def test_get_account_pnl(dex_client):
#     dex_client.account.get_account_pnl = AsyncMock()
#     result = await dex_client.get_account_pnl()
#     assert result is not None
#     assert dex_client.account.get_account_pnl.awaited
