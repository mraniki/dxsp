"""
 DEXSWAP Unit Test
"""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from web3 import EthereumTesterProvider, Web3

from dxsp import DexSwap
from dxsp.config import settings
from dxsp.protocols import DexClient, DexUniswap, DexZeroX
from dxsp.utils import AccountUtils, ContractUtils


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="uniswap")


@pytest.fixture(name="dex")
def DexTrader_fixture():
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
    assert settings.VALUE == "On Testing"


@pytest.mark.asyncio
async def test_get_approve(dex_client):
    symbol = "UNI"
    approve_receipt = None
    try:
        approve_receipt = await dex_client.get_approve(symbol)
        print(approve_receipt)
    except Exception as e:
        print(f"Error getting approve receipt: {e}")
    assert approve_receipt is None


@pytest.mark.asyncio
async def test_failed_get_approve(dex_client):
    with pytest.raises(ValueError, match="Approval failed"):
        await dex_client.account.get_approve(
            "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        )


@pytest.mark.asyncio
async def test_get_sign():
    pass


@pytest.mark.asyncio
async def test_get_gas(dex_client):
    """get_gas Testing"""
    mock_tx = {
        "to": "0x1234567890123456789012345678901234567890",
        "value": "1000000000000000000",
    }
    result = await dex_client.account.get_gas(mock_tx)
    print(result)
    assert result is not None


@pytest.mark.asyncio
async def test_get_gas_price(dex_client):
    result = await dex_client.account.get_gas_price()
    print(f"gas_price: {result}")
    assert result is not None
