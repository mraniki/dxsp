import pytest
from dxsp import DexSwap


@pytest.mark.asyncio
async def test_init_dex():
    """Init Testing"""
    exchange = DexSwap()
    check = "DexSwap" in str(type(exchange))
    assert check is True
    
    
@pytest.mark.asyncio
async def test_init_chain():
    """chain Testing"""
    exchange = DexSwap(chain_id=10)
    check = False
    if exchange.chain_id == 10:
        check = True
    assert check is True
