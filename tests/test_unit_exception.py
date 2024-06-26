"""
 DEXSWAP Unit Test
"""

import pytest

from dxsp import DexSwap
from dxsp.config import settings
#from dxsp.handler.uniswap import UniswapHandler


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="exception")


# @pytest.fixture(name="dex")
# def DexSwap_fixture():
#     return DexSwap()


def test_dynaconf_is_in_exception():
    print(settings.VALUE)
    assert settings.VALUE == "exception"



@pytest.mark.asyncio
async def test_moduledisabled(caplog):
    """Init Testing"""
    DexSwap()
    print(settings.dxsp_enabled)
    assert "Loaded 0 clients" in caplog.text


# @pytest.mark.asyncio
# async def test_uniswap_exception(dex, caplog):
#     """Init Testing"""
#     UniswapHandler()
#     assert "Loaded 0 clients" in caplog.text
