"""
 DEXSWAP Unit Test
"""
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import re
import pytest
import time
from dxsp.config import settings
from dxsp import DexSwap
#from dxsp.protocols import DexSwapUniswapV2

@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="test_uniswap_chain_1")

@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"
    assert settings.dex_chain_id == 1

@pytest.mark.asyncio
async def test_router(dex):
    router_setup = await dex.router_contract()
    router = dex.router
    print(f"router: {router}")
    assert router is not None

@pytest.mark.asyncio
async def test_quoter(dex):
    quoter_setup = await dex.quoter_contract()
    quoter = dex.quoter
    print(f"router: {quoter}")
    assert quoter is not None


@pytest.mark.asyncio
async def test_get_quote_uniswap(dex):
    quote = await dex.get_quote("WBTC")
    print(f"quote: {quote}")
    assert quote is not None
    assert quote.startswith("🦄")


# @pytest.mark.asyncio
# async def test_get_swap_uniswap(dex):
#     asset_out_address = "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"
#     asset_in_address = "0xdac17f958d2ee523a2206206994597c13d831ec7"
#     amount = 100

#     # Create a mock object for self.get_quote_uniswap()
#     get_quote_mock = AsyncMock()
#     get_quote_mock.return_value = [50]

#     # Create a mock object for self.w3.eth.get_block()
#     get_block_mock = AsyncMock()
#     get_block_mock.return_value = {"timestamp": 1000}

#     # Set up the test instance
#     dex.get_quote = get_quote_mock
#     dex.w3.eth.get_block = get_block_mock
#     dex.wallet_address = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
#     dex.protocol_type = "uniswap_v2"

    # Call the function being tested
    # swap_order = await dex.get_swap(
    #     dex.w3.to_checksum_address(asset_out_address),
    #     dex.w3.to_checksum_address(asset_in_address),
    #     amount)
    # print(f"swap_order: {swap_order}")
    # # Check the output
    # assert swap_order is not None
