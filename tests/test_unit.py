"""
 DEXSWAP Unit Test
"""
from unittest.mock import AsyncMock, patch

import pytest
from web3 import EthereumTesterProvider, Web3

from dxsp import DexTrader
from dxsp.config import settings
from dxsp.protocols import DexClient


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="uniswap")


@pytest.fixture(name="dextrader")
def DexTrader_fixture():
    return DexTrader()


@pytest.fixture(name="dex")
def DexClient_fixture(dextrader):
    return dextrader.dex_info[0]["client"]


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


@pytest.fixture(name="test_contract")
def mock_contract(dex):
    contract = AsyncMock()
    contract.get_token_decimals.return_value = 18
    contract.to_wei.return_value = 1000000000000000000
    contract.functions.balanceOf = AsyncMock(return_value=100)
    contract.wait_for_transaction_receipt.return_value = {"status": 1}
    return contract


# @pytest.fixture(name="mock_dex")
# def mock_dex_transaction():
#     dex = DexTrader()
#     dex.w3.eth.get_transaction_count = AsyncMock(return_value=1)
#     dex.get_gas = AsyncMock(return_value=21000)
#     dex.get_gas_price = AsyncMock(return_value=1000000000)
#     dex.w3.eth.account.sign_transaction = (
#         AsyncMock(return_value=AsyncMock(rawTransaction=b'signed_transaction')))
#     dex.w3.eth.send_raw_transaction = AsyncMock(return_value=b'transaction_hash')
#     return dex


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"


@pytest.mark.asyncio
async def test_dextrader(dextrader):
    """Init Testing"""
    print(dextrader)
    print(dextrader.dex_info)
    assert isinstance(dextrader, DexTrader)
    assert dextrader.commands is not None
    assert dextrader.dex_info is not None


@pytest.mark.asyncio
async def test_dex(dex):
    """Init Testing"""

    print(dex)
    assert dex is not None
    assert isinstance(dex, DexClient)
    assert dex.w3 is not None
    assert dex.w3.net.version == "1"
    assert dex.protocol_type is not None
    assert dex.protocol_type == "uniswap"
    assert dex.account.wallet_address.startswith("0x")
    assert dex.account.wallet_address == "0x1a9C8182C09F50C8318d769245beA52c32BE35BC"
    assert dex.account.private_key.startswith("0x")
    assert "1 - 32BE35BC" in dex.account.account_number


@pytest.mark.asyncio
async def test_execute_order(dextrader, order):
    result = await dextrader.execute_order(order)
    print(f"swap_order: {result}")
    assert result is not None


@pytest.mark.asyncio
async def test_execute_order_invalid(dextrader, invalid_order):
    result = await dextrader.execute_order(invalid_order)
    print(result)
    assert result.startswith("⚠️ order execution: Invalid Token")


@pytest.mark.asyncio
async def test_get_quote(dextrader):
    """getquote Testing"""
    result = await dextrader.get_quote("UNI")
    print(result)
    assert result is not None
    assert result.startswith("🦄")


@pytest.mark.asyncio
async def test_get_quote_BTC(dextrader) -> str:
    """test token account."""

    result = await dextrader.get_quote("WBTC")
    print(result)
    assert result is not None


@pytest.mark.asyncio
async def test_get_quote_invalid(dextrader):
    result = await dextrader.get_quote("THISISNOTATOKEN")
    print(result)
    assert result is not None
    assert "⚠️" in result


@pytest.mark.asyncio
async def test_get_info(dextrader):
    result = await dextrader.get_info()
    print(result)
    assert result is not None
    assert "⚠️" in result


@pytest.mark.asyncio
async def test_get_name(dextrader):
    result = await dextrader.get_name()
    print(result)
    assert result is not None
    assert "⚠️" in result


@pytest.mark.asyncio
async def test_get_balance(dextrader):
    result = await dextrader.get_balance()
    print(result)
    assert result is not None
    assert "⚠️" in result
