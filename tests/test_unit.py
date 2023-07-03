"""
 DEXSWAP Unit Test
"""
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import re
import pytest
import time
import eth_tester
from dxsp.config import settings
from dxsp import DexSwap


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="uniswap")

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


@pytest.fixture(name="invalid_order")
def invalid_order_fixture():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'NOTATHING',
        'quantity': 1,
    }

@pytest.fixture
async def quoter(dex):
    """quoter"""
    return await dex.quoter()

@pytest.fixture(name="test_contract")
def mock_contract(dex):
    contract = AsyncMock()
    contract.get_token_decimals.return_value = 18
    contract.to_wei.return_value = 1000000000000000000
    contract.functions.balanceOf = AsyncMock(return_value=100)
    contract.wait_for_transaction_receipt.return_value = {"status": 1}
    return contract

@pytest.fixture(name="mock_dex")
def mock_dex_transaction():
    dex = DexSwap()
    dex.w3.eth.get_transaction_count = AsyncMock(return_value=1)
    dex.get_gas = AsyncMock(return_value=21000)
    dex.get_gas_price = AsyncMock(return_value=1000000000)
    dex.w3.eth.account.sign_transaction = AsyncMock(return_value=AsyncMock(rawTransaction=b'signed_transaction'))
    dex.w3.eth.send_raw_transaction = AsyncMock(return_value=b'transaction_hash')
    return dex


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
async def test_execute_order(dex, order):
    sell_balance = AsyncMock()
    dex.get_swap = AsyncMock()
    result = await dex.execute_order(order)
    print(f"swap_order: {result}")
    assert result is not None


@pytest.mark.asyncio
async def test_execute_order_invalid(dex, invalid_order):
    result = await dex.execute_order(invalid_order)
    print(result)
    assert result.startswith("⚠️")


@pytest.mark.asyncio
async def test_get_swap_invalid(dex):
    with pytest.raises(ValueError):
        dex = DexSwap()
        swap_order = await dex.get_swap(
            "WBTC",
            "USDT",
            1)
        print(swap_order)


@pytest.mark.asyncio
async def test_get_quote(dex):
    """getquote Testing"""
    result = await dex.get_quote("UNI")
    print(result)
    assert result is not None
    assert result.startswith("🦄")


@pytest.mark.asyncio
async def test_get_quote_invalid(dex):
    result = await dex.get_quote("THISISNOTATOKEN")
    assert result is not None
    assert result.startswith("⚠️")

@pytest.mark.asyncio
async def test_get_approve(dex):
    symbol = "UNI"
    approve_receipt = None
    try:
        approve_receipt = await dex.get_approve(symbol)
        print(approve_receipt)
    except Exception as e:
        print(f"Error getting approve receipt: {e}")
    assert approve_receipt is None


@pytest.mark.asyncio
async def test_failed_get_approve(dex):
   with pytest.raises(ValueError, match='Approval failed'):
        result = await dex.get_approve("0xdAC17F958D2ee523a2206206994597C13D831ec7")


@pytest.mark.asyncio
async def test_get_confirmation(dex):
    result = await dex.get_confirmation("0xda56e5f1a26241a03d3f96740989e432ca41ae35b5a1b44bcb37aa2cf7772771")
    print(result)
    assert result is not None
    assert result['timestamp'] is not None
    assert result['fee'] is not None
    assert result['confirmation'] is not None
    assert result['confirmation'].startswith('➕')
    assert '⛽' in result['confirmation']
    assert '🗓️' in result['confirmation']
    assert 'ℹ️' in result['confirmation']

@pytest.mark.asyncio
async def test_get(dex):
    result = await dex.get(
        "http://ip.jsontest.com",
        params=None,
        headers=None)
    assert result is not None


@pytest.mark.asyncio
async def test_get_name(dex):
    result = await dex.get_name()
    assert isinstance(result, str)
    assert len(result) == 8


@pytest.mark.asyncio
async def test_get_info(dex):
    result = await dex.get_info()
    assert result is not None


@pytest.mark.asyncio
async def test_search_contract_address(dex):
    result = await dex.search_contract_address("USDT")
    assert result is not None
    assert result == "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    print(result)


@pytest.mark.asyncio
async def test_invalid_search_contract_address(dex):
    with pytest.raises(ValueError, match='Invalid Token'):
        await dex.search_contract_address("NOTATHING")


@pytest.mark.asyncio
async def test_get_abi(dex, mocker):
    mock_resp = {"status": "1", "result": "0x0123456789abcdef"}
    mocker.patch.object(dex, "get", return_value=mock_resp)
    result = await dex.get_explorer_abi("0x1234567890123456789012345678901234567890")
    assert result == "0x0123456789abcdef"


@pytest.mark.asyncio
async def test_invalid_get_abi(dex):
    result = await dex.get_explorer_abi("0x1234567890123456789012345678901234567890")
    assert result is None


@pytest.mark.asyncio
async def test_get_token_contract(dex):
    """get_token_contract Testing"""
    result = await dex.get_token_contract("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")
    print(type(result))
    assert result is not None
    assert type(result) is not None
    assert result.functions is not None


@pytest.mark.asyncio
async def test_get_decimals(dex):
    """get_token_decimals Testing"""
    result = await dex.get_token_decimals("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")
    print(result)
    time.sleep(5)
    assert result is not None
    assert result == 18

@pytest.mark.asyncio
async def test_get_decimals_stable(dex):
    """get_token_decimals Testing"""
    result = await dex.get_token_decimals("0xdAC17F958D2ee523a2206206994597C13D831ec7")
    print(result)
    time.sleep(5)
    assert result is not None
    assert result == 6


@pytest.mark.asyncio
async def test_get_gas(dex):
    """get_gas Testing"""
    mock_tx = {"to": "0x1234567890123456789012345678901234567890",
                "value": "1000000000000000000"}
    result = await dex.get_gas(mock_tx)
    print(result)


@pytest.mark.asyncio
async def test_get_gas_price(dex):
    # Call the get_gasPrice method
    result = await dex.get_gas_price()
    print(f"gas_price: {result}")
    assert result is not None


@pytest.mark.asyncio
async def test_get_account_balance(dex):
    # Call the get_account_balance method
    result = await dex.get_account_balance()
    assert result is not None
    assert result >= 0


@pytest.mark.asyncio
async def test_get_token_balance(dex):
    # Call the get_token_balance method
    result = await dex.get_token_balance("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")
    print("balance ", result)
    assert result is not None
    assert result >= 0
    assert isinstance(result, int)