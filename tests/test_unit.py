import pytest
from web3 import Web3
import requests
import re
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
async def test_router(exchange):
    return await exchange.router()


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
async def test_get(exchange):
    result = await exchange._get(
        "http://ip.jsontest.com",
        params=None,
        headers=None)
    assert result is not None


@pytest.mark.asyncio
async def test_get_router(exchange):
    router = exchange.router()
    assert router is not None


@pytest.mark.asyncio
async def test_quoter(exchange):
    """quoter Testing"""
    quoter = await exchange.quoter()
    if quoter:
        assert quoter is not None


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
async def test_get_token_abi():
    dex_erc20_abi_url = "https://raw.githubusercontent.com/web3/web3.js/4.x/fixtures/build/ERC20Token.json"
    token_abi = requests.get(dex_erc20_abi_url).text
    assert token_abi is not None


@pytest.mark.asyncio
async def test_get_abi(exchange, mocker):
    # Mock the _get method to return a mock response
    mock_resp = {"status": "1", "result": "0x0123456789abcdef"}
    mocker.patch.object(exchange, "_get", return_value=mock_resp)

    # Call the get_abi method and check the result
    abi = await exchange.get_abi("0x1234567890123456789012345678901234567890")

    assert abi == "0x0123456789abcdef"


@pytest.mark.asyncio
async def test_get_token_contract(exchange):
    """get_token_contract Testing"""
    contract = await exchange.get_token_contract("WBTC")
    if contract:
        assert contract is not None
        assert type(contract) is exchange.w3.eth.contract


@pytest.mark.asyncio
async def test_get_quote(exchange):
    """getquote Testing"""
    quote = await exchange.get_quote("WBTC")
    if quote:
        assert quote is not None
        assert quote.startswith("🦄")


@pytest.mark.asyncio
async def test_get_quote_uniswap(exchange):
    # Call the get_quote_uniswap method and check the result
    quote = await exchange.get_quote_uniswap(
        exchange.w3.to_checksum_address("0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"),
        exchange.w3.to_checksum_address("0xdac17f958d2ee523a2206206994597c13d831ec7"),
        1000000000)
    print(f"quote: {quote}")
    assert quote is not None
    assert quote.startswith("🦄")
    expected_quote_pattern = r"🦄 \d+ USDT"
    assert re.match(expected_quote_pattern, quote) is not None


# @pytest.mark.asyncio
# async def test_get_approve_uniswap(exchange, mocker):
#     mock_token = mocker.MagicMock()
#     mock_token.allowance.return_value = 0
#     mock_token.functions.approve.return_value = "0x1234567890abcdef"

#     mocker.patch.object(
#         exchange, "get_abi", return_value="mock_abi")
#     mocker.patch.object(
#         exchange.w3.eth, "contract", return_value=mock_token)
#     mocker.patch.object(
#         exchange, "get_sign", return_value="0xabcdef1234567890")

#     # Call the get_approve_uniswap method and check the result
#     approval_txHash_complete = await exchange.get_approve_uniswap(
#         "0x1234567890123456789012345678901234567890")
#     print(f"approval_txHash_complete: {approval_txHash_complete}")
#     assert approval_txHash_complete is not None


# @pytest.mark.asyncio
# async def test_get_swap_uniswap(mocker):
#     exchange = DexSwap()
#     mock_swap_order = mocker.MagicMock()
#     mock_swap_order.return_value = "0x1234567890abcdef"

#     mock_router_functions = mocker.MagicMock(swapExactTokensForTokens=mock_swap_order)
#     mock_router = mocker.MagicMock()
#     mock_router.functions = mock_router_functions

#     mocker.patch.object(exchange, "get_abi", return_value="mock_abi")
#     mocker.patch.object(exchange.w3.eth, "contract", return_value=mock_router)

#     # Call the get_swap_uniswap method and check the result
#     swap_order = await exchange.get_swap_uniswap(
#         "0x1234567890123456789012345678901234567890",
#         "0x0987654321098765432109876543210987654321",
#         100000000)

#     print(f"swap_order: {swap_order}")
#     assert swap_order is not None


@pytest.mark.asyncio
async def test_get_gas(exchange):
    # Create a mock transaction
    mock_tx = {"to": "0x1234567890123456789012345678901234567890",
               "value": "1000000000000000000"}

    # Call the get_gas method and check the result
    gas_estimate = await exchange.get_gas(mock_tx)
    assert gas_estimate > 1


# @pytest.mark.asyncio
# async def test_get_swap(exchange):
#     swap = await exchange.get_swap(
#         "WBTC",
#         "USDT",
#         1)
#     print(f"swap: {swap}")
#     assert swap is not None
