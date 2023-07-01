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


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="test_zerox_chain_1")

@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "test_zerox"
    assert settings.dex_chain_id == 1


@pytest.fixture(name="order")
def order_params_fixture():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'WBTC',
        'quantity': 1,
    }


@pytest.mark.asyncio
async def test_dex(dex):
    """Init Testing"""
    assert isinstance(dex, DexSwap)
    assert dex.w3 is not None
    assert dex.chain_id is not None
    assert dex.protocol_type is not None
    assert dex.protocol_type == "0x"
    assert dex.wallet_address.startswith("0x")
    assert dex.wallet_address == "0x1a9C8182C09F50C8318d769245beA52c32BE35BC"
    assert dex.private_key.startswith("0x")
    assert dex.account == "1 - 32BE35BC"


@pytest.mark.asyncio
async def test_get_0x_quote(dex):
    result = await dex.get_quote("UNI")
    print(result)
    assert result is not None


@pytest.mark.asyncio
async def test_get_0x_quote_fail(dex):
    with pytest.raises(ValueError,match="Invalid Token"):
        result = await dex.get_quote("NOTATHING")
        assert result is None


@pytest.mark.asyncio
async def test_failed_get_approve(dex):
   with pytest.raises(ValueError, match='Approval failed'):
       result = await dex.get_approve("0xdAC17F958D2ee523a2206206994597C13D831ec7")