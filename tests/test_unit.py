import pytest
# import responses
from web3 import Web3
from unittest.mock import AsyncMock
from dxsp import DexSwap

@pytest.fixture
def exchange():
    return DexSwap()

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
async def test_init_dex(exchange):
    """Init Testing"""
    check = "DexSwap" in str(type(exchange))
    assert check is True
    assert exchange.w3 is not None
    assert exchange.chain_id is not None
    assert exchange.protocol_type is not None
    assert exchange.protocol_type == "uniswap_v2"
    assert exchange.wallet_address.startswith("0x")
    assert exchange.private_key.startswith("0x")
    assert exchange.cg_platform is not None


@pytest.mark.asyncio
async def test_get_quote(exchange):
    """getquote Testing"""
    quote = await exchange.get_quote("WBTC")
    if quote:
        assert quote is not None
        assert quote.startswith("0x")


@pytest.mark.asyncio
async def test_search_contract(exchange):
    address = await exchange.search_contract("WBTC")
    assert address.startswith("0x")
    # assert address == "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"

    address = await exchange.search_contract("USDT")
    assert address is not None
    assert address.startswith("0x")
    # assert address == "0xdac17f958d2ee523a2206206994597c13d831ec7"

    address = await exchange.search_contract("UNKNOWN")
    assert address == "no contract found for UNKNOWN"


@pytest.mark.asyncio
async def test_get_token_contract(exchange):
    """get_token_contract Testing"""
    contract = await exchange.get_token_contract("WBTC")
    if contract:
        assert contract is not None
        assert type(contract) is exchange.w3.eth.contract


@pytest.mark.asyncio
async def test_router(exchange):
    """router Testing"""
    router = await exchange.router()
    if router:
        assert router is not None


@pytest.mark.asyncio
async def test_quoter(exchange):
    """router Testing"""
    quoter = await exchange.quoter()
    if quoter:
        assert quoter is not None


@pytest.mark.asyncio
async def test_logger(caplog):
    for record in caplog.records:
        assert record.levelname != "CRITICAL"
        assert "wally" not in caplog.text


@pytest.mark.asyncio
async def test_get(exchange):
    result = await exchange._get(
        "http://ip.jsontest.com",
        params=None,
        headers=None)

    assert result is not None


@pytest.mark.asyncio
async def test_get_quote_uniswap_v2(mocker,exchange):
    # Arrange
    mock_router = (
        mocker.patch.object(exchange, 'router', return_value=AsyncMock()))
    result = await mock_router.get_quote_uniswap(
        'asset_in_address',
        'asset_out_address')
    assert result is not None


@pytest.mark.asyncio
async def test_get_gas(exchange):
    # Create a mock transaction
    mock_tx = {"to": "0x1234567890123456789012345678901234567890",
               "value": "1000000000000000000"}

    # Call the get_gas method and check the result
    gas_estimate = await exchange.get_gas(mock_tx)
    assert gas_estimate > 1


# @pytest.mark.asyncio
# async def test_uniswap_v2_get_swap(exchange):
#     # Call get_swap with some input parameters
#     result = await exchange.get_swap('ETH', 'DAI', 10)
#     assert result is not None


# @pytest.mark.asyncio
# async def test_get_confirmation(mocker):

#     exchange = DexSwap()
#     mocker.patch('DexSwap', autospec=True)
#     web3 = exchange.w3
#     order_hash = AsyncMock(return_value=100)
#     order_hash_details = AsyncMock(return_value=100)
#     asset_out_symbol = AsyncMock(return_value=100)
#     asset_out_address = AsyncMock(return_value=100)
#     order_amount = AsyncMock(return_value=100)
#     order_hash = AsyncMock(return_value=100)
#     web3.eth.get_transaction_receipt.return_value = {'gasUsed': 123}
#     web3.eth.get_block.return_value = {'timestamp': 1234567890}

#     # Call the function
#     result = await DexSwap.get_confirmation(
    # order_hash, order_hash_details,
    # asset_out_symbol, asset_out_address,
    # order_amount)

#     # Assertions
#     assert result['id'] is not None
#     assert result['timestamp'] is not None
#     assert result['instrument'] == asset_out_symbol
#     assert result['contract'] == asset_out_address
#     assert result['amount'] == order_amount
#     assert result['fee'] is not None
#     assert result['price'] == "TBD"
#     assert "Size" in result['confirmation']
#     assert "Entry" in result['confirmation']
#     assert trade['id'] in result['confirmation']
#     assert trade['datetime'] in result['confirmation']

# @pytest.mark.asyncio
# @responses.activate
# async def test_get_block_explorer_status():
#     exchange = DexSwap()
#     # Define the mock response from the block explorer API
#     response_body = {"status": "1"}
#     responses.add(responses.GET,
#                   "https://www.example.com/api",
#                   json=response_body)

#     # Call the get_block_explorer_status method and check the result
#     status = await exchange.get_block_explorer_status("0x1234567890abcdef")
#     assert status == "1"

#     # Verify that the mock API was called with the correct URL
#     assert len(responses.calls) == 1
#     assert responses.calls[0].request.url == "https://www.example.com/api?module=transaction&action=gettxreceiptstatus&txhash=0x1234567890abcdef&apikey=12345"
