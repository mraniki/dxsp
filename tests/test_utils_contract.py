# """
#  DEXSWAP Unit Test
# """
import decimal
import time
from unittest.mock import AsyncMock, patch

import pytest
from web3 import EthereumTesterProvider, Web3

import dxsp
from dxsp import DexSwap
from dxsp.config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="uniswap")


@pytest.fixture(name="dex")
def DexTrader_fixture():
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


@pytest.fixture(name="test_contract")
def mock_contract(dex):
    contract = AsyncMock()
    contract.get_token_decimals.return_value = 18
    contract.to_wei.return_value = 1000000000000000000
    contract.functions.balanceOf = AsyncMock(return_value=100)
    contract.wait_for_transaction_receipt.return_value = {"status": 1}
    return contract


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"


# @pytest.mark.asyncio
# async def test_search_contract_address(dex):
#     for dx in dex.dex_info:
#         result = await dx.contract_utils.search_contract_address("USDT")
#         assert result is not None
#         assert result == "0xdAC17F958D2ee523a2206206994597C13D831ec7"
#         print(result)


# @pytest.mark.asyncio
# async def test_invalid_search_contract_address(dex):
#     for dx in dex.dex_info:
#         result = await dx.contract_utils.search_contract_address("NOTATHING")
#         assert result is None


# @pytest.mark.asyncio
# async def test_get_token_name(dex):
#     """get_token_symbol Testing"""
#     for dx in dex.dex_info:
#         result = await dx.contract_utils.get_token_name(
#             "0xdAC17F958D2ee523a2206206994597C13D831ec7"
#         )
#         print(result)
#         assert result is not None
#         assert result == "Tether USD"


# @pytest.mark.asyncio
# async def test_get_token_symbol(dex):
#     """get_token_symbol Testing"""
#     for dx in dex.dex_info:
#         result = await dx.contract_utils.get_token_symbol(
#             "0xdAC17F958D2ee523a2206206994597C13D831ec7"
#         )
#         print(result)
#         assert result is not None
#         assert result == "USDT"


# @pytest.mark.asyncio
# async def test_get_decimals(dex):
#     """get_token_decimals Testing"""
#     for dx in dex.dex_info:
#         result = await dx.contract_utils.get_token_decimals(
#             "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
#         )
#         print(result)
#         time.sleep(5)
#         assert result is not None
#         assert result == 18


# @pytest.mark.asyncio
# async def test_get_decimals_stable(dex):
#     """get_token_decimals Testing"""
#     for dx in dex.dex_info:
#         result = await dx.contract_utils.get_token_decimals(
#             "0xdAC17F958D2ee523a2206206994597C13D831ec7"
#         )
#         print(result)
#         time.sleep(5)
#         assert result is not None
#         assert result == 6


# @pytest.mark.asyncio
# async def test_get_token_contract(dex):
#     """get_token_contract Testing"""
#     for dx in dex.dex_info:
#         result = await dx.contract_utils.get_token_contract(
#             "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
#         )
#         print(type(result))
#         assert result is not None
#         assert type(result) is not None
#         assert result.functions is not None


# @pytest.mark.asyncio
# async def test_get_abi(dex, mocker):
#     for dx in dex.dex_info:
#         mock_resp = {"status": "1", "result": "0x0123456789abcdef"}
#         mocker.patch.object(dxsp.utils.explorer_utils, "get", return_value=mock_resp)
#         result = await dx.contract_utils.get_explorer_abi(
#             "0x1234567890123456789012345678901234567890"
#         )
#         assert result == "0x0123456789abcdef"


# @pytest.mark.asyncio
# async def test_invalid_get_abi(dex):
#     for dx in dex.dex_info:
#         result = await dx.contract_utils.get_explorer_abi(
#             "0x1234567890123456789012345678901234567890"
#         )
#         assert result is None


# @pytest.mark.asyncio
# async def test_get_token_balance(dex):
#     # Call the get_token_balance method
#     for dx in dex.dex_info:
#         result = await dx.contract_utils.get_token_balance(
#             "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", dx.wallet_address
#         )
#         print("balance ", result)
#         print("balance ", type(result))
#         assert result is not None
#         assert result >= 0
#         assert isinstance(result, decimal.Decimal)


# @pytest.mark.asyncio
# async def test_token_balance(account, dex) -> str:
#     """test token account."""
#     for dx in dex.dex_info:
#         result = await dx.get_trading_asset_balance()
#         print(result)
#         assert result is not None


# @pytest.mark.asyncio
# async def calculate_sell_amount(dex):
#     pass


# @pytest.mark.asyncio
# async def test_get_confirmation(dex):
#     for dx in dex.dex_info:
#         result = await dx.contract_utils.get_confirmation(
#             "0xda56e5f1a26241a03d3f96740989e432ca41ae35b5a1b44bcb37aa2cf7772771"
#         )
#         print(result)
#         assert result is not None
#         assert result["timestamp"] is not None
#         assert result["fee"] is not None
#         assert result["confirmation"] is not None
#         assert result["confirmation"].startswith("➕")
#         assert "⛽" in result["confirmation"]
#         assert "🗓️" in result["confirmation"]
#         assert "ℹ️" in result["confirmation"]
