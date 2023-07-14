"""
 DEXSWAP Uniswap  Test
"""

import pytest
from dxsp.config import settings
from dxsp import DexSwap

@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="uniswap")

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
    assert settings.VALUE == "On Testing"


@pytest.mark.asyncio
async def test_get_quote(dex):
    result = await dex.get_quote("WBTC")
    print(f"result: {result}")
    assert result is not None
    assert result.startswith("🦄")


@pytest.mark.asyncio
async def test_get_swap(dex, order):
    result = await dex.execute_order(order)
    print(f"result: {result}")
    assert result is not None
