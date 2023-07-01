"""
 DEXSWAP Web3 oriented unit test
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock

from web3 import Web3, EthereumTesterProvider
from eth_tester import PyEVMBackend, EthereumTester

from dxsp.config import settings
from dxsp import DexSwap


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="test_uniswap_chain_1")

@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()

@pytest.fixture(name="order")
def order_params_fixture():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'WBTC',
        'quantity': 1,
    }

@pytest.fixture
def tester_provider():
  return EthereumTesterProvider()

@pytest.fixture(name="web3")
def w3():
    provider = EthereumTesterProvider()
    return Web3(provider)

@pytest.fixture()
def account(web3) -> str:
  """Deploy account."""
  return web3.eth.accounts[0]

def test_account(account) -> str:
  """Deploy account."""
  print(account)
  assert account is not None

def test_account_balance(account) -> str:
    """Deploy account."""
    with patch("dxsp.config.settings", autospec=True):
        settings.wallet_address = account

        dex = DexSwap()
        print(dex.wallet_address)
        balance = dex.get_account_balance()
        print(balance)
        assert balance is not None
