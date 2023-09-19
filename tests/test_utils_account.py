"""
 DEXSWAP Unit Test
"""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from web3 import EthereumTesterProvider, Web3

from dxsp import DexSwap
from dxsp.config import settings
from dxsp.protocols import DexClient, DexUniswap, DexZeroX


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="uniswap")


@pytest.fixture(name="dex")
def DexTrader_fixture():
    return DexSwap()

@pytest.fixture(name="dex_client")
def mock_dex_client():
    # Create a mock DexClient object
    dex_client = Mock(spec=DexClient)
    
    # Set any desired return values or side effects for the DexClient methods
    dex_client.get_quote.return_value = 100
    dex_client.get_swap.side_effect = (
        lambda sell_address, buy_address, amount: amount * 2)
    
    return dex_client

@pytest.fixture
def tester_provider():
    return EthereumTesterProvider()


@pytest.fixture(name="web3")
def w3():
    provider = EthereumTesterProvider()
    return Web3(provider)


@pytest.fixture(name="account")
def account_fixture(web3) -> str:
    """setup account."""
    return web3.eth.accounts[0]


@pytest.fixture(name="order")
def order_params_fixture():
    """Return order parameters."""
    return {
        "action": "BUY",
        "instrument": "WBTC",
        "quantity": 1,
    }


@pytest.fixture(name="invalid_order")
def invalid_order_fixture():
    """Return order parameters."""
    return {
        "action": "BUY",
        "instrument": "NOTATHING",
        "quantity": 1,
    }


@pytest.fixture(name="test_contract")
def mock_contract(dex):
    contract = AsyncMock()
    contract.get_token_decimals.return_value = 18
    contract.to_wei.return_value = 1000000000000000000
    contract.functions.balanceOf = AsyncMock(return_value=100)
    contract.wait_for_transaction_receipt.return_value = {"status": 1}
    return contract


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"


@pytest.mark.asyncio
async def test_get_approve(dex_client):
    symbol = "UNI"
    approve_receipt = None
    try:
            approve_receipt = await dex_client.get_approve(symbol)
            print(approve_receipt)
    except Exception as e:
        print(f"Error getting approve receipt: {e}")
    assert approve_receipt is None


# @pytest.mark.asyncio
# async def test_failed_get_approve(dex):
#     with pytest.raises(ValueError, match="Approval failed"):
#         for dx in dex.dex_info:
#             await dx.account.get_approve("0xdAC17F958D2ee523a2206206994597C13D831ec7")


@pytest.mark.asyncio
async def test_get_sign():
    pass


@pytest.mark.asyncio
async def test_get_gas(dex_client):
    """get_gas Testing"""
    mock_tx = {
        "to": "0x1234567890123456789012345678901234567890",
        "value": "1000000000000000000",
    }
    result = await dex_client.account.get_gas(mock_tx)
    print(result)


@pytest.mark.asyncio
async def test_get_gas_price(dex_client):
    result = await dex_client.account.get_gas_price()
    print(f"gas_price: {result}")
    assert result is not None
