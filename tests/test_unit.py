import pytest
from dxsp import DexSwap


@pytest.mark.asyncio
async def test_init_dex():
    """Init Testing"""
    exchange = DexSwap()
    check = "DexSwap" in str(type(exchange))
    assert check is True


@pytest.mark.asyncio
# async def test_get_quote():
#     """getquote Testing"""
#     exchange = DexSwap()
#     check = await exchange.get_quote("WBTC")
#     print(check)
#     if check:
#         check = True
#     assert check is True
