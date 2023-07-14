"""
 DEXSWAP Unit Test
"""

import pytest
from dxsp.config import settings
from dxsp import DexSwap


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="bsc")

@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


@pytest.fixture(name="order")
def order_params_fixture():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'WBTC',
        'quantity': 1,
    }


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "chain_56"
    assert settings.dex_wallet_address == "0xf977814e90da44bfa03b6295a0616a897441acec"
    assert settings.dex_notify_invalid_token is False

@pytest.mark.asyncio
async def test_get_quote(dex):
    """getquote Testing"""
    print(settings.VALUE)
    quote = await dex.get_quote("BTCB")
    print(quote)
    if quote:
        assert settings.VALUE == "chain_56"
        assert dex.w3.net.version == '56'
        assert quote is not None
        assert quote.startswith("🦄")


@pytest.mark.asyncio
async def test_execute_order(dex, order):
    result = await dex.execute_order(order)
    print(f"result: {result}")
    assert result is not None
