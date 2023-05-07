import pytest
from dxsp import DexSwap


@pytest.mark.asyncio
async def test_init_dex():
    """Init Testing"""
    exchange = DexSwap()
    check = "DexSwap" in str(type(exchange))
    assert check is True


@pytest.mark.asyncio
async def test_get_quote():
    """getquote Testing"""
    exchange = DexSwap()
    quote = await exchange.get_quote("WBTC")
    print(quote)
    if quote:
        assert quote is not None


@pytest.mark.asyncio
async def test_search_contract():
    """search_contract Testing"""
    exchange = DexSwap()
    contract = await exchange.search_contract("WBTC")
    print(contract)
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
    print(contract)
    if contract:
        assert contract is not None
        assert type(contract) is exchange.w3.eth.contract
