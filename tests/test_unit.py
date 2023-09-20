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
    settings.configure(FORCE_ENV_FOR_DYNACONF="dxsp")


@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


@pytest.fixture(name="dex_client")
def mock_dex_client():
    return DexUniswap(
        name="uniswap",
        wallet_address="0x1a9C8182C09F50C8318d769245beA52c32BE35BC",
        private_key="0xdeadbeet45ab87712ad64ccb3b10217737f7faacbf2872e88fdd9a537d8fe266",
        protocol_type="uniswap",
        protocol_version=2,
        api_endpoint=None,
        api_key=None,
        router_contract_addr="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        factory_contract_addr="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        trading_asset_address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
        trading_slippage=2,
        trading_risk_amount=10,
        block_explorer_url="https://api.etherscan.io/api?",
        block_explorer_api=None,
        w3=Web3(Web3.HTTPProvider("https://rpc.ankr.com/eth")),
    )


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
        assert dx.account.wallet_address.startswith("0x")


@pytest.mark.asyncio
async def test_get_quote(dex):
    """getquote Testing"""
    print(dex.dex_info)
    result = await dex.get_quote("UNI")
    print(result)
    assert result is not None
    assert "🦄" in result


@pytest.mark.asyncio
async def test_get_quote_invalid(dex):
    result = await dex.get_quote("THISISNOTATOKEN")
    print(result)
    assert result is not None
    assert "Quote failed" in result


@pytest.mark.asyncio
async def test_get_swap(dex_client):
    result = await dex_client.get_swap("USDT", "UNI", 1)
    print(f"swap_order: {result}")
    assert result is not None


@pytest.mark.asyncio
async def test_execute_order(dex, order):
    result = await dex.execute_order(order)
    print(f"swap_order: {result}")
    assert result is not None


@pytest.mark.asyncio
async def test_execute_order_invalid(dex, invalid_order):
    result = await dex.execute_order(invalid_order)
    print(result)
    assert "⚠️" in result


@pytest.mark.asyncio
async def test_get_info(dex):
    result = await dex.get_info()
    print(result)
    assert result is not None
    assert "ℹ️" in result


@pytest.mark.asyncio
async def test_get_help(dex):
    result = await dex.get_help()
    print(result)
    assert result is not None
    assert "🎯" in result


@pytest.mark.asyncio
async def test_calculate_sell_amount(dex_client):
    result = await dex_client.calculate_sell_amount(
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        dex_client.wallet_address,
        1,
    )
    print(result)
    assert result is not None


@pytest.mark.asyncio
async def test_get_balance(dex):
    result = await dex.get_account_balance()
    print(result)
    assert result is not None
    assert "💵" in result


# @pytest.mark.asyncio
# async def test_get_trading_asset_balance(dex):
#     result = await dex.get_trading_asset_balance()
#     print(result)
#     assert result is not None


@pytest.mark.asyncio
async def test_get_account_position(dex):
    result = await dex.get_account_position()
    print(result)
    assert result is not None
    assert "📊" in result


# @pytest.mark.asyncio
# async def test_get_account_transactions(dex):
#     result = await dex.get_account_transactions()
#     print(result)
#     assert result is not None


# @pytest.mark.asyncio
# async def test_get_account_pnl(dex):
#     result = await dex.get_account_pnl()
#     print(result)
#     assert result is not None
