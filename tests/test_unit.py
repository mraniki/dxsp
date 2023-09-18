"""
 DEXSWAP Unit Test
"""
from unittest.mock import AsyncMock, patch

import pytest
from web3 import EthereumTesterProvider, Web3

from dxsp import DexSwap
from dxsp.config import settings
from dxsp.protocols import DexUniswap, DexZeroX


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="uniswap")


@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


@pytest.fixture
def tester_provider():
    return EthereumTesterProvider()


@pytest.fixture(name="web3")
def w3():
    provider = EthereumTesterProvider()
    return Web3(provider)


@pytest.fixture(name="account")
def account_fixture(web3) -> str:
    """setup account."""
    return web3.eth.accounts[0]


@pytest.fixture(name="order")
def order_params_fixture():
    """Return order parameters."""
    return {
        "action": "BUY",
        "instrument": "WBTC",
        "quantity": 1,
    }


@pytest.fixture(name="invalid_order")
def invalid_order_fixture():
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
    assert dex.commands is not None
    assert dex.dex_info is not None
    for dx in dex.dex_info:
        print(dx)
        assert dx is not None
        assert dx.name is not None
        assert dx.protocol_type == "uniswap"
        assert dx.private_key.startswith("0x")


# @pytest.mark.asyncio
# async def test_dex(dex):
#     """Init Testing"""
#     print(dex)
#     assert dex is not None
#     assert isinstance(dex, DexClient)
#     assert dex.w3 is not None
#     assert dex.w3.net.version == "1"
#     assert dex.protocol_type is not None
#     assert dex.protocol_type == "uniswap"
#     assert dex.account.wallet_address.startswith("0x")
#     assert dex.account.wallet_address == "0x1a9C8182C09F50C8318d769245beA52c32BE35BC"
#     assert dex.account.private_key.startswith("0x")
#     assert "1 - 32BE35BC" in dex.account.account_number


# @pytest.mark.asyncio
# async def test_execute_order(dex, order):
#     result = await dex.execute_order(order)
#     print(f"swap_order: {result}")
#     assert result is not None


# @pytest.mark.asyncio
# async def test_execute_order_invalid(dex, invalid_order):
#     result = await dex.execute_order(invalid_order)
#     print(result)
#     assert result.startswith("⚠️ order execution: Invalid Token")


@pytest.mark.asyncio
async def test_get_quote(dex):
    """getquote Testing"""
    print(dex.dex_info)
    result = await dex.get_quote("UNI")
    print(result)
    assert result is not None
    assert "🦄" in result


# @pytest.mark.asyncio
# async def test_get_quote_invalid(dex):
#     result = await dex.get_quote("THISISNOTATOKEN")
#     print(result)
#     assert result is not None
#     assert "⚠️" in result


@pytest.mark.asyncio
async def test_get_info(dex):
    result = await dex.get_info()
    print(result)
    assert result is not None
    assert "ℹ️" in result


# @pytest.mark.asyncio
# async def test_get_balance(dex):
#     result = await dex.get_balance()
#     print(result)
#     assert result is not None
#     assert "⚠️" in result
