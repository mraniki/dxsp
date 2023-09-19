# """
#  DEXSWAP Unit Test
# """
import decimal
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
from web3 import EthereumTesterProvider, Web3

import dxsp
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


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"


@pytest.mark.asyncio
async def test_search_contract_address(dex_client):
    result = await dex_client.contract_utils.search_contract_address("USDT")
    assert result is not None
    assert result == "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    print(result)


@pytest.mark.asyncio
async def test_invalid_search_contract_address(dex_client):
    result = await dex_client.contract_utils.search_contract_address("NOTATHING")
    assert result is None


@pytest.mark.asyncio
async def test_get_token_name(dex_client):
    """get_token_symbol Testing"""
    result = await dex_client.contract_utils.get_token_name(
        "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    )
    print(result)
    assert result is not None
    assert "Tether USD" in result


@pytest.mark.asyncio
async def test_get_token_symbol(dex_client):
    """get_token_symbol Testing"""
    result = await dex_client.contract_utils.get_token_symbol(
        "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    )
    print(result)
    assert result is not None
    assert result == "USDT"


@pytest.mark.asyncio
async def test_get_decimals(dex_client):
    """get_token_decimals Testing"""
    result = await dex_client.contract_utils.get_token_decimals(
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
    )
    print(result)
    time.sleep(5)
    assert result is not None
    assert result == 18


@pytest.mark.asyncio
async def test_get_decimals_stable(dex_client):
    """get_token_decimals Testing"""
    result = await dex_client.contract_utils.get_token_decimals(
        "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    )
    print(result)
    time.sleep(5)
    assert result is not None
    assert result == 6


@pytest.mark.asyncio
async def test_get_token_contract(dex_client):
    result = await dex_client.contract_utils.get_token_contract(
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
    )
    print(type(result))
    assert result is not None
    assert type(result) is not None
    assert result.functions is not None


# @pytest.mark.asyncio
# async def test_get_abi(dex, mocker):
#         mock_resp = {"status": "1", "result": "0x0123456789abcdef"}
#         mocker.patch.object(dxsp.utils.explorer_utils, "get", return_value=mock_resp)
#         result = await dx.contract_utils.get_explorer_abi(
#             "0x1234567890123456789012345678901234567890"
#         )
#         assert result == "0x0123456789abcdef"


# @pytest.mark.asyncio
# async def test_invalid_get_abi(dex_client):
#     result = await dex_client.contract_utils.get_explorer_abi(
#         "0x1234567890123456789012345678901234567890"
#     )
#     assert result is None


@pytest.mark.asyncio
async def test_get_token_balance(dex_client):
    # Call the get_token_balance method
    result = await dex_client.contract_utils.get_token_balance(
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", dex_client.wallet_address
    )
    print("balance ", result)
    print("balance ", type(result))
    assert result is not None
    assert result >= 0
    assert isinstance(result, decimal.Decimal)


@pytest.mark.asyncio
async def test_token_balance(account, dex_client) -> str:
    """test token account."""
    result = await dex_client.get_trading_asset_balance()
    print(result)
    assert result is not None


@pytest.mark.asyncio
async def test_calculate_sell_amount(dex_client):
    result = await dex_client.contract_utils.calculate_sell_amount(
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        dex_client.wallet_address,
        1,
    )
    print(result)
    assert result is not None


@pytest.mark.asyncio
async def test_get_confirmation(dex_client):
    result = await dex_client.contract_utils.get_confirmation(
        "0xda56e5f1a26241a03d3f96740989e432ca41ae35b5a1b44bcb37aa2cf7772771"
    )
    print(result)
    assert result is not None
    assert result["timestamp"] is not None
    assert result["fee"] is not None
    assert result["confirmation"] is not None
    assert "➕" in result["confirmation"]
    assert "⛽" in result["confirmation"]
    assert "🗓️" in result["confirmation"]
    assert "ℹ️" in result["confirmation"]
