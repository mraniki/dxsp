"""
 DEXSWAP Unit Test
"""

from unittest.mock import AsyncMock

import pytest
from web3 import EthereumTesterProvider, Web3

from dxsp import DexSwap
from dxsp.config import settings
from dxsp.protocols import DexUniswap


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
        protocol="uniswap",
        protocol_version=2,
        api_endpoint=None,
        api_key=None,
        router_contract_addr="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        factory_contract_addr="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        trading_asset_address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
        trading_slippage=2,
        trading_risk_amount=10,
        trading_risk_percentage=True,
        trading_asset_separator="",
        block_explorer_url="https://api.etherscan.io/api?",
        block_explorer_api=None,
        w3=Web3(Web3.HTTPProvider("https://eth.llamarpc.com")),
        mapping=None,
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


@pytest.fixture(name="invalid_order")
def invalid_order_fixture():
    """Return order parameters."""
    return "not an order"


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"


@pytest.mark.asyncio
async def test_dextrader(dex):
    """Init Testing"""
    assert isinstance(dex, DexSwap)
    assert dex.clients is not None
    assert isinstance(dex, DexSwap)
    assert callable(dex.get_balances)
    assert callable(dex.get_positions)
    assert callable(dex.submit_order)

    for dx in dex.clients:
        assert dx is not None
        assert dx.name is not None
        assert dx.protocol in ["uniswap", "0x", "kwenta"]
        assert dx.private_key.startswith("0x")
        assert dx.wallet_address.startswith("0x")
        assert callable(dx.replace_instrument)
        assert callable(dx.get_instrument_address)
        assert callable(dx.get_order_amount)
        assert callable(dx.get_quote)
        assert callable(dx.get_swap)
        assert callable(dx.make_swap)
        assert callable(dx.get_account_balance)
        assert callable(dx.get_trading_asset_balance)
        assert callable(dx.get_account_margin)
        assert callable(dx.get_account_position)
        assert callable(dx.get_account_open_positions)
        assert callable(dx.get_account_pnl)
        if dx.protocol == "0x":
            assert dx.api_key is not None


@pytest.mark.asyncio
async def test_get_info(dex):
    result = await dex.get_info()
    #print(result)
    assert result is not None
    assert "ℹ️" in result
    assert ("1" in result) or ("56" in result)


@pytest.mark.asyncio
async def test_get_quote(dex):
    """getquote Testing"""
    print(dex.clients)
    get_quote = AsyncMock()
    replace_instrument = AsyncMock()
    result = await dex.get_quotes("BTC")
    #print(result)
    assert result is not None
    assert "🦄" in result
    assert get_quote.awaited
    assert replace_instrument.awaited
    assert ("eth" in result) or ("bsc" in result)
    assert "2" in result
    numerical_count = sum(1 for char in result if char.isdigit())
    assert numerical_count >= 10


@pytest.mark.asyncio
async def test_get_balances(dex):
    get_account_balance = AsyncMock()
    result = await dex.get_balances()
    #print(result)
    assert result is not None
    assert "🏦" in result
    assert get_account_balance.awaited
    assert ("1" in result) or ("56" in result)


@pytest.mark.asyncio
async def test_get_positions(dex):
    get_account_position = AsyncMock()
    result = await dex.get_positions()
    #print(result)
    assert result is not None
    assert "📊" in result
    assert "Opened" in result
    assert "Margin" in result
    assert get_account_position.awaited
    assert ("1" in result) or ("56" in result)


@pytest.mark.asyncio
async def test_get_pnls(dex):
    get_account_pnl = AsyncMock()
    result = await dex.get_pnl()
    #print(result)
    assert result is not None
    assert "🏆" in result
    assert get_account_pnl.awaited
    assert ("1" in result) or ("56" in result)


@pytest.mark.asyncio
async def test_get_order_amount(dex_client):
    result = await dex_client.get_order_amount(
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        dex_client.wallet_address,
        1,
    )
    print(result)
    assert result is not None


@pytest.mark.asyncio
async def test_submit_order(dex, order):
    result = await dex.submit_order(order)
    #print(f"swap_order: {result}")
    assert result is not None


@pytest.mark.asyncio
async def test_submit_order_invalid(dex, invalid_order):
    result = await dex.submit_order(invalid_order)
    #print(result)
    assert "⚠️" in result


@pytest.mark.asyncio
async def test_get_swap(dex_client):
    result = await dex_client.get_swap("USDT", "UNI", 1)
    #print(f"swap_order: {result}")
    assert result is not None
