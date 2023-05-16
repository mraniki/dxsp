import pytest
from web3 import Web3
from unittest.mock import AsyncMock
from dxsp import DexSwap


@pytest.fixture
def web3():
    # create a mock web3 instance
    return Web3(Web3.EthereumTesterProvider())


@pytest.fixture
def asset_in_address():
    # create a mock asset in address
    return "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"  # UNI token address


@pytest.fixture
def asset_out_address():
    # create a mock asset out address
    return "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"  # WETH token address


@pytest.fixture
def router(web3):
    # create a mock router contract
    return web3.eth.contract(abi=..., address=...)


@pytest.fixture
def token_contract(web3):
    # create a mock token contract
    return web3.eth.contract(abi=..., address=...)


@pytest.fixture
def swap_contract(web3):
    # create a mock swap contract
    return web3.eth.contract(abi=..., address=...)


@pytest.mark.asyncio
async def test_init_dex():
    """Init Testing"""
    exchange = DexSwap()
    check = "DexSwap" in str(type(exchange))
    assert check is True
    assert exchange.w3 is not None
    assert exchange.chain_id is not None
    assert exchange.protocol_type is not None
    assert exchange.wallet_address.startswith("0x")
    assert exchange.private_key.startswith("0x")
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


@pytest.mark.asyncio
async def test_quoter():
    """router Testing"""
    exchange = DexSwap()
    quoter = await exchange.quoter()
    if quoter:
        assert quoter is not None


@pytest.mark.asyncio
async def test_logger(caplog):
    exchange = DexSwap()
    for record in caplog.records:
        assert record.levelname != "CRITICAL"
        assert "wally" not in caplog.text


@pytest.mark.asyncio
async def test_get():
    test_class = DexSwap()
    result = await test_class._get(
        "http://ip.jsontest.com",
        params=None,
        headers=None)

    assert result is not None


@pytest.mark.asyncio
async def test_get_quote_uniswap_v2(mocker):
    # Arrange
    instance = DexSwap()
    instance.protocol_type = "uniswap_v2"
    mock_router = (
        mocker.patch.object(instance, 'router', return_value=AsyncMock()))
    result = await mock_router.get_quote_uniswap(
        'asset_in_address',
        'asset_out_address')
    assert result is not None
