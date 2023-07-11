"""
 DEXSWAP Unit Test
"""

import pytest
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
    assert settings.dex_wallet_address == "0xf977814e90da44bfa03b6295a0616a897441acec"
    assert settings.dex_notify_invalid_token is False

@pytest.mark.asyncio
async def test_get_quote(dex):
    """getquote Testing"""
    print(settings.VALUE)
    quote = await dex.get_quote("BTCB")
    print(quote)
    if quote:
        assert settings.VALUE
        assert dex.w3.net.version == '56'
        assert quote is not None
        assert quote.startswith("🦄")


@pytest.mark.asyncio
async def test_no_notify_invalid_token_(dex):
    assert settings.VALUE == "chain_56"
    result = await dex.search_contract_address("NOTATHING")
    assert result is None
