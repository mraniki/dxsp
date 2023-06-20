"""
 DEXSWAP Unit Test
"""
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import re
import pytest
import time
from dxsp import DexSwap
from dxsp.config import settings


@pytest.fixture(name="dex_1")
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")

@pytest.fixture(name="dex")
def DexSwap_fixture(dex_1):
    return DexSwap()

@pytest.fixture(name="testnet")
def set_test_settings_DEX5():
    settings.configure(FORCE_ENV_FOR_DYNACONF="chain_5")


@pytest.fixture(name="dex_56")
def set_test_settings_DEX56():
    settings.configure(FORCE_ENV_FOR_DYNACONF="chain_56")

def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"
    assert settings.dex_chain_id == 1
    assert settings.dex_wallet_address == "0x1234567890123456789012345678901234567899"


def test_dynaconf_is_in_testing_env_DEX5(testnet):
    print(settings.VALUE)
    assert settings.VALUE == "On Testnet"
    assert settings.dex_chain_id == 5
    assert settings.dex_wallet_address == "0x1234567890123456789012345678901234567890"

def test_dynaconf_is_in_testing_env_DEX56(dex_56):
    print(settings.VALUE)
    assert settings.VALUE == "DEX chain_56"
    assert settings.dex_chain_id == 56
    assert settings.dex_wallet_address == "0x1234567890123456789012345678901234568888"


@pytest.fixture(name="order")
def order_params_fixture():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'WBTC',
        'quantity': 1,
    }

@pytest.fixture(name="order_56")
def buy_UNI_order():
    return {'action': 'BUY', 'instrument': 'BTCB', 'quantity': 1}

@pytest.fixture(name="wrong_order")
def wrong_order_fixture():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'NOTATHING',
        'quantity': 1,
    }

@pytest.fixture
async def router(dex, dex_1):
    """router"""
    return await dex.router()


@pytest.fixture
async def quoter(dex, dex_1):
    """quoter"""
    return await dex.quoter()

@pytest.fixture
def mock_contract():
    contract = MagicMock()
    contract.get_token_decimals.return_value = 18
    contract.to_wei.return_value = 1000000000000000000
    contract.wait_for_transaction_receipt.return_value = {"status": 1}
    return contract


@pytest.mark.asyncio
async def test_dex(dex_1):
    """Init Testing"""
    dex = DexSwap()
    assert isinstance(dex, DexSwap)
    assert dex.w3 is not None
    assert dex.chain_id is not None
    assert dex.protocol_type is not None
    assert dex.protocol_type == "uniswap_v2"
    assert dex.wallet_address.startswith("0x")
    assert dex.wallet_address == "0x1234567890123456789012345678901234567899"
    assert dex.private_key.startswith("0x")
    assert dex.account == "1 - 34567899"


def test_dex_swap_chain_56(dex_56):
    dex = DexSwap()
    assert isinstance(dex, DexSwap)
    assert dex.w3 is not None
    assert dex.wallet_address == "0x1234567890123456789012345678901234568888"
    assert dex.private_key == "0xdeadbeef"
    assert dex.account == "56 - 34568888"
    assert dex.chain_id == 56



@pytest.mark.asyncio
async def test_execute_order(dex_1, order):
    dex = DexSwap()
    sell_balance = AsyncMock()
    dex.get_swap = AsyncMock()
    swap_order = await dex.execute_order(order)
    print(f"swap_order: {swap_order}")
    assert swap_order is not None


@pytest.mark.asyncio
async def test_execute_order_invalid(dex_1, wrong_order):
    with pytest.raises(ValueError,match="Order execution failed"):
        dex = DexSwap()
        swap_order = await dex.execute_order(wrong_order)
        print(swap_order)


@pytest.mark.asyncio
async def test_nomoney_execute_order_chain56(dex_56, order):
    dex = DexSwap()
    swap_order = await dex.execute_order(order)
    print(swap_order)
    assert swap_order == "No Money"

@pytest.mark.asyncio
async def test_get_swap_chain56(dex_56):
    dex = DexSwap()
    order = await dex.get_swap("USDT", "BTCB", 1)
    assert order == "No Money"

@pytest.mark.asyncio
async def test_execute_order_chain56(dex_56, order_56):
    dex = DexSwap()
    swap_order = await dex.execute_order(order_56)
    print(f"swap_order: {swap_order}")
    assert swap_order is not None

@pytest.mark.asyncio
async def test_get_swap(dex):
    # with pytest.raises(ValueError,match="No Money"):
    get_quote_mock = MagicMock()
    get_quote_mock.return_value = [50]

    get_block_mock = MagicMock()
    get_block_mock.return_value = {"timestamp": 1000}
    dex.get_approve = AsyncMock()
    dex.get_sign = AsyncMock()
    dex.w3.to_hex = Mock()
    dex.w3.wait_for_transaction_receipt= MagicMock(return_value={"status": 1})
    dex.get_confirmation = AsyncMock(return_value={
        "confirmation": (
            "➕ Size: 100\n"
            "⚫️ Entry: 100\n"
            "ℹ️ 0xxxx\n"
            "🗓️ ---"
        )
    })
    dex.get_quote_uniswap = get_quote_mock
    dex.w3.eth.get_block = get_block_mock


    sell_token = "USDT"
    buy_token = "WBTC"
    amount = 100

    # Call the function being tested
    swap_order = await dex.get_swap(
        sell_token,
        buy_token,
        amount)
    print(f"swap_order: {swap_order}")
# Check the output
    assert swap_order is not None



async def test_get_swap_invalid(dex_1):
    with pytest.raises(ValueError):
        dex = DexSwap()
        swap_order = await dex.get_swap(
            "WBTC",
            "USDT",
            1)
        print(swap_order)


@pytest.mark.asyncio
async def test_get_quote(dex, dex_1):
    """getquote Testing"""
    quote = await dex.get_quote("UNI")
    print(quote)
    if quote:
        assert quote is not None
        assert quote.startswith("🦄")


@pytest.mark.asyncio
async def test_get_quote_invalid(dex):
    """Test get_quote() method"""
    quote = await dex.get_quote("THISISNOTATOKEN")
    assert quote == "contract not found"


@pytest.mark.asyncio
async def test_get_approve(dex):
    result = await dex.get_approve("TOKEN")
    assert result is None


@pytest.mark.asyncio
async def test_get_sign(dex_1):
    dex = DexSwap()
    dex.w3.eth.account.sign_transaction = Mock()
    dex.w3.eth.send_raw_transaction = Mock()
    mock_tx = {"to": "0x1234567890123456789012345678901234567890",
        "value": "1000000000000000000"}
    result = await dex.get_sign(mock_tx)
    assert result is not None


@pytest.mark.asyncio
async def test_get_confirmation(dex):
    result = await dex.get_confirmation("0xda56e5f1a26241a03d3f96740989e432ca41ae35b5a1b44bcb37aa2cf7772771")
    print(result)
    assert result is not None
    assert result['confirmation'] is not None
    assert result['confirmation'].startswith('➕')


@pytest.mark.asyncio
async def test_get(dex):
    result = await dex.get(
        "http://ip.jsontest.com",
        params=None,
        headers=None)
    assert result is not None


@pytest.mark.asyncio
async def test_router(dex):
    router = await dex.router()
    assert router is not None


@pytest.mark.asyncio
async def test_quoter(dex):
    """quoter Testing"""
    quoter = await dex.quoter()
    if quoter:
        assert quoter is not None


@pytest.mark.asyncio
async def test_get_name(dex):
    name = await dex.get_name()
    assert isinstance(name, str)
    assert len(name) == 8


@pytest.mark.asyncio
async def test_search_address(dex):
    # address = await dex.search_contract("WBTC")
    # print(address)
    # assert address == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"

    address = await dex.search_contract("USDT")
    assert address is not None
    assert address == "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    print(address)


@pytest.mark.asyncio
async def test_get_abi(dex, mocker):
    # Mock the _get method 
    mock_resp = {"status": "1", "result": "0x0123456789abcdef"}
    mocker.patch.object(dex, "get", return_value=mock_resp)

    abi = await dex.get_abi("0x1234567890123456789012345678901234567890")

    assert abi == "0x0123456789abcdef"


@pytest.mark.asyncio
async def test_get_abi_invalid(dex):
    abi = await dex.get_abi("0x1234567890123456789012345678901234567890")
    assert abi is None


@pytest.mark.asyncio
async def test_get_token_contract(dex):
    """get_token_contract Testing"""
    contract = await dex.get_token_contract("UNI")
    print(contract)
    print(type(contract))
    print(contract.functions)
    if contract:
        assert contract is not None
        assert type(contract) is not None
        assert contract.functions is not None


@pytest.mark.asyncio
async def test_get_decimals(dex):
    """get_token_decimals Testing"""
    token_decimals = await dex.get_token_decimals("UNI")
    print(token_decimals)
    time.sleep(5)
    if token_decimals:
        assert token_decimals is not None
        assert token_decimals ==18


@pytest.mark.asyncio
async def test_get_gas(dex):
   # with pytest.raises(ValueError):
        # Create a mock transaction
        mock_tx = {"to": "0x1234567890123456789012345678901234567890",
                "value": "1000000000000000000"}

        # Call the get_gas method and check the result
        gas_estimate = await dex.get_gas(mock_tx)
        print(gas_estimate)


@pytest.mark.asyncio
async def test_get_gas_price(dex):
    # Call the get_gasPrice method and check the result
    gas_price = await dex.get_gas_price()
    print(f"gas_price: {gas_price}")
    assert gas_price is not None


@pytest.mark.asyncio
async def test_get_account_balance(dex):
    # Call the get_account_balance method and check the result
    balance = await dex.get_account_balance()
    assert balance is not None
    assert balance >= 0


@pytest.mark.asyncio
async def test_get_token_balance(dex):
    # Call the get_token_balance method and check the result
    with patch("dxsp.config.settings", autospec=True) as mock_settings:
        mock_settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
    token_balance = await dex.get_token_balance("UNI")
    print("balance ", token_balance)
    assert token_balance is not None
    assert token_balance == 0
    # assert isinstance(token_balance, int)


@pytest.mark.asyncio
async def test_get_quote_uniswap(dex):
    # Call the get_quote_uniswap method and check the result
    quote = await dex.get_quote_uniswap(
        dex.w3.to_checksum_address("0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"),
        dex.w3.to_checksum_address("0xdac17f958d2ee523a2206206994597c13d831ec7"),
        1000000000)
    print(f"quote: {quote}")
    assert quote is not None
    assert quote.startswith("🦄")
    expected_quote_pattern = r"🦄 \d+ USDT"
    assert re.match(expected_quote_pattern, quote) is not None


@pytest.mark.asyncio
async def test_get_approve_uniswap(dex):
    symbol = "UNI"
    approve_receipt = None
    try:
        approve_receipt = await dex.get_approve_uniswap(symbol)
        print(approve_receipt)
    except Exception as e:
        print(f"Error getting approve receipt: {e}")
    assert approve_receipt is None



@pytest.mark.asyncio
async def test_get_swap_uniswap(dex):
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
    dex.get_quote_uniswap = get_quote_mock
    dex.w3.eth.get_block = get_block_mock
    dex.wallet_address = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    dex.protocol_type = "uniswap_v2"

    # Call the function being tested
    swap_order = await dex.get_swap_uniswap(
        asset_out_address,
        asset_in_address,
        amount)
    print(f"swap_order: {swap_order}")
    # Check the output
    assert swap_order is not None


@pytest.mark.asyncio
async def test_get_0x_quote(dex):
    with patch("dxsp.config.settings", autospec=True):
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_chain_id = 1
        settings.dex_rpc = "https://rpc.ankr.com/eth_goerli"
        settings.dex_0x_url = "https://goerli.api.0x.org"
        settings.dex_protocol_type = "0x"
        # Test function ETH > UNI
        result = await dex.get_0x_quote(
            "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
            1)
        assert result is not None
        #assert isinstance(result, float)


@pytest.mark.asyncio
async def test_get_0x_quote_fail(dex):
    with patch("dxsp.config.settings", autospec=True):
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_chain_id = 1
        settings.dex_rpc = "https://rpc.ankr.com/eth_goerli"
        settings.dex_0x_url = "https://goerli.api.0x.org"
        settings.dex_protocol_type = "0x"
        # Test function DAI > UNI
        result = await dex.get_0x_quote(
            "0xE68104D83e647b7c1C15a91a8D8aAD21a51B3B3E",
            "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
            1)
        assert result is None
