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
    settings.configure(FORCE_ENV_FOR_DYNACONF="bsc")

@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "chain_56"
    assert settings.dex_chain_id == 56
    assert settings.dex_wallet_address == "0xf977814e90da44bfa03b6295a0616a897441acec"


@pytest.mark.asyncio
async def test_get_quote(dex):
    """getquote Testing"""
    print(settings.VALUE)
    print(dex.w3.net.version)
    quote = await dex.get_quote("BTCB")
    print(quote)
    if quote:
        assert settings.VALUE
        assert dex.w3.net.version == '56'
        assert quote is not None
        assert quote.startswith("🦄")
