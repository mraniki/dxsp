"""
 DEXSWAP Unit Test
"""

import pytest

from dxsp import DexSwap
from dxsp.config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="kwenta")


@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


@pytest.fixture(name="order")
def order_params_fixture():
    """Return order parameters."""
    return {
        "action": "BUY",
        "instrument": "WBTC",
        "quantity": 1,
    }


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "test_kwenta"


@pytest.mark.asyncio
async def test_dex(dex):
    """Init Testing"""
    assert isinstance(dex, DexSwap)
    for dx in dex.dex_info:
        assert dx is not None
        assert dx.w3 is not None
        assert dx.protocol_type is not None
        assert dx.protocol_type == "kwenta"


@pytest.mark.asyncio
async def test_get_quote(dex):
    result = await dex.get_quotes("UNI")
    assert result is not None
    assert "🦄" in result


@pytest.mark.asyncio
async def test_submit_order(dex, order):
    result = await dex.submit_order(order)
    print(result)
    assert result is not None
    assert "⚠️" in result
