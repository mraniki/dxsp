import pytest
from web3 import Web3
import requests
import re
from dxsp import DexSwap
from dxsp.config import settings
from unittest.mock import patch, MagicMock


@pytest.fixture
def exchange():
    return DexSwap()


@pytest.fixture
async def router(exchange):
    return await exchange.router()

@pytest.fixture
async def quoter(exchange):
    return await exchange.quoter()


@pytest.mark.asyncio
async def test_init_dex():
    """Init Testing"""
    exchange = DexSwap()
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
def test_settings_dex_swap_init():
    with patch("dxsp.config.settings", autospec=True):
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567890"
        settings.dex_private_key = "0xdeadbeef"

        dex = DexSwap()
        assert dex.wallet_address == "0x1234567890123456789012345678901234567890"
        assert dex.private_key == "0xdeadbeef"



@pytest.mark.asyncio
async def test_get(exchange):
    result = await exchange._get(
        "http://ip.jsontest.com",
        params=None,
        headers=None)
    assert result is not None


@pytest.mark.asyncio
async def test_router(exchange):
    router = await exchange.router()
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
async def test_get_no_mock(exchange):
    abi = await exchange.get_abi("0x1234567890123456789012345678901234567890")
    assert abi is None

@pytest.mark.asyncio
async def test_get_token_contract(exchange):
    """get_token_contract Testing"""
    contract = await exchange.get_token_contract("UNI")
    print(contract)
    print(type(contract))
    print(contract.functions)
    if contract:
        assert contract is not None
        assert type(contract) is not None
        assert contract.functions is not None


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


@pytest.mark.asyncio
async def test_get_swap_uniswap(exchange):
    asset_out_address = "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"
    asset_in_address = "0xdac17f958d2ee523a2206206994597c13d831ec7"
    amount = 100

    # Create a mock object for self.get_quote_uniswap()
    get_quote_mock = MagicMock()
    get_quote_mock.return_value = [50]

    # Create a mock object for self.w3.eth.get_block()
    get_block_mock = MagicMock()
    get_block_mock.return_value = {"timestamp": 1000}

    # Set up the test instance
    exchange.get_quote_uniswap = get_quote_mock
    exchange.w3.eth.get_block = get_block_mock
    exchange.wallet_address = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    exchange.protocol_type = "uniswap_v2"

    # Call the function being tested
    swap_order = await exchange.get_swap_uniswap(
        asset_out_address,
        asset_in_address,
        amount)
    print(f"swap_order: {swap_order}")
    # Check the output
    assert swap_order is not None



@pytest.mark.asyncio
async def test_get_gas(exchange):
    # Create a mock transaction
    mock_tx = {"to": "0x1234567890123456789012345678901234567890",
               "value": "1000000000000000000"}

    # Call the get_gas method and check the result
    gas_estimate = await exchange.get_gas(mock_tx)
    assert gas_estimate > 1


@pytest.mark.asyncio
async def test_get_gas_price(exchange):
    # Call the get_gasPrice method and check the result
    gas_price = await exchange.get_gas_price()
    print(f"gas_price: {gas_price}")
    assert gas_price is not None


@pytest.mark.asyncio
async def test_no_money_get_swap(exchange):
    swap = await exchange.get_swap(
        "WBTC",
        "USDT",
        1)
    print(f"swap: {swap}")
    assert swap.__class__ == ValueError
    assert str(swap) == "No Money"

@pytest.mark.asyncio
async def test_get_account_balance(exchange):
    # Call the get_account_balance method and check the result
    balance = await exchange.get_account_balance()
    assert balance is not None
    assert balance >= 0


@pytest.mark.asyncio
async def test_get_token_balance(exchange):
    # Call the get_token_balance method and check the result
    token_balance = await exchange.get_token_balance("UNI")
    assert isinstance(token_balance, int)
    assert token_balance >= 0
