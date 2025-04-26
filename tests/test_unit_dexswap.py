"""
 DEXSWAP Unit Test
"""

from unittest.mock import AsyncMock

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
        if dx.name == "eth":
            return dx


@pytest.fixture(name="dex_client_zero_x")
def client_zero_x_fixture(dex):
    for dx in dex.clients:
        if dx.protocol == "zerox":
            return dx


@pytest.fixture(name="order")
def order_params_fixture():
    """Return order parameters."""
    return {
        "action": "BUY",
        "instrument": "BTC",
        "quantity": 1,
    }


@pytest.fixture(name="invalid_symbol")
def invalid_symbol_fixture():
    """Return order parameters."""
    return {
        "action": "BUY",
        "instrument": "NOTATHING",
        "quantity": 1,
    }

def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"


@pytest.mark.asyncio
async def test_dextrader(dex):
    """Init Testing"""
    assert isinstance(dex, DexSwap)
    assert dex.clients is not None
    assert callable(dex.get_info)
    assert callable(dex.get_balances)
    assert callable(dex.get_positions)
    assert callable(dex.get_pnls)
    assert callable(dex.submit_order)

    for dx in dex.clients:
        assert dx is not None
        assert dx.name is not None
        assert dx.protocol in ["uniswap", "zerox", "kwenta"]
        assert callable(dx.get_order_amount)
        assert callable(dx.replace_instrument)
        assert callable(dx.get_quote)
        assert callable(dx.get_swap)
        assert callable(dx.make_swap)
        assert callable(dx.get_account_balance)
        assert callable(dx.get_trading_asset_balance)
        assert callable(dx.get_account_margin)
        assert callable(dx.get_account_position)
        assert callable(dx.get_account_open_positions)
        assert callable(dx.get_account_pnl)
        if dx.protocol == "zerox":
            assert dx.api_key is not None
            # assert dx.api_endpoint is not None # Obsolete for v2


@pytest.mark.asyncio
async def test_get_info(dex):
    result = await dex.get_info()
    assert result is not None
    print(result)
    assert "ℹ️" in result
    assert ("1" in result) or ("56" in result)


@pytest.mark.asyncio
async def test_get_balances(dex):
    get_account_balance = AsyncMock()
    result = await dex.get_balances()
    assert result is not None
    assert get_account_balance.awaited
    assert ("1" in result) or ("56" in result) or ("137" in result)


@pytest.mark.asyncio
async def test_get_positions(dex):
    get_account_position = AsyncMock()
    result = await dex.get_positions()
    assert result is not None
    assert "Opened" in result
    assert "Margin" in result
    assert get_account_position.awaited
    assert ("1" in result) or ("56" in result)


@pytest.mark.asyncio
async def test_get_pnls(dex):
    get_account_pnl = AsyncMock()
    result = await dex.get_pnls()
    assert result is not None
    assert get_account_pnl.awaited
    assert ("eth" in result) or ("pol" in result)


@pytest.mark.asyncio
async def test_get_quotes(dex):
    """getquote Testing"""
    get_quote = AsyncMock()
    result = await dex.get_quotes(symbol="WBTC")
    assert result is not None
    assert isinstance(result, str)
    assert get_quote.awaited
    assert ("eth" in result)
    assert ("bsc" in result)
    assert ("pol" in result)


@pytest.mark.asyncio
async def test_get_quotes_invalid(dex):
    """getquote Testing"""
    result = await dex.get_quotes(symbol="NOTATOKEN")
    assert "⚠️ Token" in result
    assert "not found" in result

@pytest.mark.asyncio
async def test_submit_order(dex, order):
    result = await dex.submit_order(order)
    print(result)
    assert result is not None
    assert ("eth" in result) or ("pol" in result)
    assert ("⚠️" in result) or ("⛽" in result)


@pytest.mark.asyncio
async def test_submit_invalid_symbol(dex, invalid_symbol):
    result = await dex.submit_order(invalid_symbol)
    assert result is not None
    assert "⚠️" in result
