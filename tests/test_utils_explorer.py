"""
 DEXSWAP Unit Test
"""
from unittest.mock import AsyncMock
import pytest
import dxsp
from dxsp.config import settings
from dxsp import DexSwap
from web3 import Web3, EthereumTesterProvider
from dxsp.utils.utils import get
from dxsp.utils.explorer_utils import get_explorer_abi, get_account_transactions


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="uniswap")


@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


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
    dex.w3.eth.account.sign_transaction = (
        AsyncMock(return_value=AsyncMock(rawTransaction=b'signed_transaction')))
    dex.w3.eth.send_raw_transaction = AsyncMock(return_value=b'transaction_hash')
    return dex


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"



@pytest.mark.asyncio
async def test_get():
    result = await get(
        "http://ip.jsontest.com",
        params=None,
        headers=None)
    assert result is not None


@pytest.mark.asyncio
async def test_get_abi(dex, mocker):
    mock_resp = {"status": "1", "result": "0x0123456789abcdef"}
    mocker.patch.object(dxsp.utils.explorer_utils, "get", return_value=mock_resp)
    result = await get_explorer_abi("0x1234567890123456789012345678901234567890")
    assert result == "0x0123456789abcdef"


@pytest.mark.asyncio
async def test_invalid_get_abi():
    result = await get_explorer_abi("0x1234567890123456789012345678901234567890")
    assert result is None


@pytest.mark.asyncio
async def test_get_account_transactions(dex):
    # Call the get_account_transactions method
    result = await get_account_transactions(
        '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        dex.account.wallet_address)
    print(f"history: {result}")
    assert result is not None
    assert 'pnl' in result
    assert 'tokenList' in result