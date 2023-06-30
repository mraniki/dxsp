"""
 DEXSWAP Unit Test
"""
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import re
import pytest
import time
from dxsp.config import settings
from dxsp import DexSwap



@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")

@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"
    assert settings.dex_chain_id == 1


@pytest.fixture(name="order")
def order_params_fixture():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'WBTC',
        'quantity': 1,
    }


@pytest.fixture(name="wrong_order")
def wrong_order_fixture():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'NOTATHING',
        'quantity': 1,
    }

@pytest.fixture
async def router(dex):
    """router"""
    return await dex.router()

@pytest.fixture
async def quoter(dex):
    """quoter"""
    return await dex.quoter()

@pytest.fixture(name="test_contract")
def mock_contract(dex):
    contract = MagicMock()
    contract.get_token_decimals.return_value = 18
    contract.to_wei.return_value = 1000000000000000000
    contract.wait_for_transaction_receipt.return_value = {"status": 1}
    return contract


@pytest.mark.asyncio
async def test_dex(dex):
    """Init Testing"""
    assert isinstance(dex, DexSwap)
    assert dex.w3 is not None
    assert dex.chain_id is not None
    assert dex.protocol_type is not None
    assert dex.protocol_type == "uniswap_v2"
    assert dex.wallet_address.startswith("0x")
    assert dex.wallet_address == "0x1a9C8182C09F50C8318d769245beA52c32BE35BC"
    assert dex.private_key.startswith("0x")
    assert dex.account == "1 - 32BE35BC"


@pytest.mark.asyncio
async def test_router_object(router):
    print(router)
    assert router is not None



@pytest.mark.asyncio
async def test_execute_order(dex, order):
    sell_balance = AsyncMock()
    dex.get_swap = AsyncMock()
    swap_order = await dex.execute_order(order)
    print(f"swap_order: {swap_order}")
    assert swap_order is not None


# @pytest.mark.asyncio
# async def test_execute_order_invalid(dex, wrong_order):
#     with pytest.raises(ValueError, match='contract not found'):
#         swap_order = await dex.execute_order(wrong_order)


@pytest.mark.asyncio
async def test_execute_order_invalid(dex, wrong_order):
    # with pytest.raises(ValueError, match='contract not found'):
    swap_order = await dex.execute_order(wrong_order)
    print(swap_order)

# @pytest.mark.asyncio
# async def test_get_swap(dex, dex_1):
#     # with pytest.raises(ValueError,match="No Money"):
#     get_quote_mock = MagicMock()
#     get_quote_mock.return_value = [50]

#     get_block_mock = MagicMock()
#     get_block_mock.return_value = {"timestamp": 1000}
#     dex.get_approve = AsyncMock()
#     dex.get_sign = AsyncMock()
#     dex.w3.to_hex = Mock()
#     dex.w3.wait_for_transaction_receipt= MagicMock(return_value={"status": 1})
#     dex.get_confirmation = AsyncMock(return_value={
#         "confirmation": (
#             "➕ Size: 100\n"
#             "⚫️ Entry: 100\n"
#             "ℹ️ 0xxxx\n"
#             "🗓️ ---"
#         )
#     })
#     dex.get_quote_uniswap = get_quote_mock
#     dex.w3.eth.get_block = get_block_mock
#     sell_token = "USDT"
#     buy_token = "WBTC"
#     amount = 100

#     # Call the function being tested
#     swap_order = await dex.get_swap(
#         sell_token,
#         buy_token,
#         amount)
#     print(f"swap_order: {swap_order}")
# # Check the output
#     assert swap_order is not None


# @pytest.mark.asyncio
# async def test_get_swap_invalid(dex_1):
#     with pytest.raises(ValueError):
#         dex = DexSwap()
#         swap_order = await dex.get_swap(
#             "WBTC",
#             "USDT",
#             1)
#         print(swap_order)


@pytest.mark.asyncio
async def test_get_quote(dex):
    """getquote Testing"""
    quote = await dex.get_quote("UNI")
    print(quote)
    if quote:
        assert quote is not None
        assert quote.startswith("🦄")


@pytest.mark.asyncio
async def test_get_quote_invalid(dex):
    with pytest.raises(ValueError, match='Invalid Token'):
        quote = await dex.get_quote("THISISNOTATOKEN")


#@pytest.mark.asyncio
#async def test_get_approve(dex):
#    result = await dex.get_approve("0xdAC17F958D2ee523a2206206994597C13D831ec7")
#    assert result is not None


# @pytest.mark.asyncio
# async def test_get_sign(dex):
#     dex = DexSwap()
#     dex.w3.eth.account.sign_transaction = Mock()
#     dex.w3.eth.send_raw_transaction = Mock()
#     mock_tx = {"to": "0x1234567890123456789012345678901234567890",
#         "value": "1000000000000000000"}
#     result = await dex.get_sign(mock_tx)
#     assert result is not None


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
async def test_search_contract_address(dex):
    address = await dex.search_contract_address("USDT")
    assert address is not None
    assert address == "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    print(address)



@pytest.mark.asyncio
async def test_invalid_search_contract_address(dex):
    with pytest.raises(ValueError, match='Invalid Token'):
        address = await dex.search_contract_address("NOTATHING")



@pytest.mark.asyncio
async def test_get_abi(dex, mocker):
    mock_resp = {"status": "1", "result": "0x0123456789abcdef"}
    mocker.patch.object(dex, "get", return_value=mock_resp)
    abi = await dex.get_abi("0x1234567890123456789012345678901234567890")
    assert abi == "0x0123456789abcdef"


@pytest.mark.asyncio
async def test_invalid_get_abi(dex):
    abi = await dex.get_abi("0x1234567890123456789012345678901234567890")
    assert abi is None


@pytest.mark.asyncio
async def test_get_token_contract(dex):
    """get_token_contract Testing"""
    contract = await dex.get_token_contract("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")
    print(type(contract))
    assert contract is not None
    assert type(contract) is not None
    assert contract.functions is not None


@pytest.mark.asyncio
async def test_get_decimals(dex):
    """get_token_decimals Testing"""
    token_decimals = await dex.get_token_decimals("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")
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
    token_balance = await dex.get_token_balance("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")
    print("balance ", token_balance)
    assert token_balance is not None
    assert token_balance >= 0
    assert isinstance(token_balance, int)



@pytest.mark.asyncio
async def test_failed_get_trading_asset_balance(dex):
    with pytest.raises(ValueError, match='No Balance'):
        token_balance = await dex.get_trading_asset_balance()

