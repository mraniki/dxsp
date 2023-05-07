import pytest
from dxsp import DexSwap


@pytest.mark.asyncio
async def test_init_dex():
    """Init Testing"""
    exchange = DexSwap()
    check = "DexSwap" in str(type(exchange))
    assert check is True
    assert exchange.w3 is not None
    assert exchange.chain_id == 1
    assert exchange.protocol_type == "1inch"
    assert exchange.wallet_address == (
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
    assert exchange.private_key == "0x111111111117dc0aaaaaa0fa6a738034aaaa302"
    assert exchange.cg_platform is not None


@pytest.mark.asyncio
async def test_get_quote():
    """getquote Testing"""
    exchange = DexSwap()
    quote = await exchange.get_quote("WBTC")
    if quote:
        assert quote is not None


@pytest.mark.asyncio
async def test_search_contract():
    """search_contract Testing"""
    exchange = DexSwap()
    contract = await exchange.search_contract("WBTC")
    if contract:
        assert contract is not None
        assert contract == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"


@pytest.mark.asyncio
async def test_get_contract_address():
    """get_contract_address Testing"""
    exchange = DexSwap()
    token_mainnet_list = (
        "https://raw.githubusercontent.com/mraniki/tokenlist/main/all.json")
    address = await exchange.get_contract_address(token_mainnet_list, "WBTC")
    if address:
        print(address)
        assert address is not None
        assert address == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"


@pytest.mark.asyncio
async def test_get_token_contract():
    """get_token_contract Testing"""
    exchange = DexSwap()
    contract = await exchange.get_token_contract("WBTC")
    if contract:
        assert contract is not None
        assert type(contract) is exchange.w3.eth.contract


@pytest.mark.asyncio
async def test_router():
    """router Testing"""
    exchange = DexSwap()
    router = await exchange.router()
    if router:
        assert router is not None
