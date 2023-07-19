"""
 DEXSWAP Unit Test
"""
import pytest

from dxsp import DexSwap
from dxsp.config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testnet")

@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testnet"
    assert settings.dex_wallet_address == "0x1a9C8182C09F50C8318d769245beA52c32BE35BC"


# @pytest.mark.asyncio
# async def test_get_quote(dex):
#     """getquote Testing"""
#     print(settings.VALUE)
#     quote = await dex.get_quote("wBTC")
#     print(quote)
#     if quote:
#         assert settings.VALUE
#         assert dex.w3.net.version == '5'
#         assert quote is not None
#         assert quote.startswith("🦄")


# @pytest.mark.asyncio
# async def test_get_swap(dex, account, order): 
#     """test token account."""
#     with patch("dxsp.config.settings", autospec=True):
#         settings.dex_wallet_address = account
#         dex = DexSwap()
#         swap_order = await dex.execute_order(order)
#         print(swap_order)


# @pytest.mark.asyncio
# async def test_get_swap_invalid(dex, order):
#     with pytest.raises(ValueError):
#         await dex.execute_order(order)