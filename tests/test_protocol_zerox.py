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
from dxsp.protocols import DexSwapZeroX

@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")

@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"
    assert settings.dex_chain_id == 1


@pytest.fixture(name="order")
def order_params_fixture():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'WBTC',
        'quantity': 1,
    }


@pytest.fixture(name="wrong_order")
def wrong_order_fixture():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'NOTATHING',
        'quantity': 1,
    }

@pytest.mark.asyncio
async def test_dex(dex):
    """Init Testing"""
    assert isinstance(dex, DexSwap)
    assert dex.w3 is not None
    assert dex.chain_id is not None
    assert dex.protocol_type is not None
    assert dex.protocol_type == "uniswap_v2"
    assert dex.wallet_address.startswith("0x")
    assert dex.wallet_address == "0x1a9C8182C09F50C8318d769245beA52c32BE35BC"
    assert dex.private_key.startswith("0x")
    assert dex.account == "1 - c3f84CEe"


@pytest.mark.asyncio
async def test_get_0x_quote(dex):
    with patch("dxsp.config.settings", autospec=True):
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_chain_id = 1
        settings.dex_rpc = "https://rpc.ankr.com/eth_goerli"
        settings.dex_0x_url = "https://goerli.api.0x.org"
        settings.dex_protocol_type = "0x"
        # Test function ETH > UNI
        result = await dex.get_0x_quote(
            "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
            1)
        assert result is not None
        #assert isinstance(result, float)


@pytest.mark.asyncio
async def test_get_0x_quote_fail(dex):
    with patch("dxsp.config.settings", autospec=True):
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_chain_id = 1
        settings.dex_rpc = "https://rpc.ankr.com/eth_goerli"
        settings.dex_0x_url = "https://goerli.api.0x.org"
        settings.dex_protocol_type = "0x"
        # Test function DAI > UNI
        result = await dex.get_0x_quote(
            "0xE68104D83e647b7c1C15a91a8D8aAD21a51B3B3E",
            "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
            1)
        assert result is None
