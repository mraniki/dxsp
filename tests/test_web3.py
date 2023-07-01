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
  """setup account."""
  return web3.eth.accounts[0]

def test_account(account) -> str:
  """test account."""
  print(account)
  assert account is not None

@pytest.mark.asyncio
async def test_account_balance(account) -> str:
    """test balance account."""
    with patch("dxsp.config.settings", autospec=True):
        settings.dex_wallet_address = account
        print(settings.dex_wallet_address)
        dex = DexSwap()
        print(dex.wallet_address)
        result = await dex.get_account_balance()
        print(result)
        assert result is not None

@pytest.mark.asyncio
async def test_token_balance(account) -> str:
    """test token account."""
    with patch("dxsp.config.settings", autospec=True):
        settings.dex_wallet_address = account
        # with pytest.raises(ValueError, match='No Balance'):
        dex = DexSwap()
        result = await dex.get_token_balance(settings.trading_asset_address)
        print(result)
        assert result is not None

@pytest.mark.asyncio
async def test_trading_asset_balance(account) -> str:
    """test token account."""
    with patch("dxsp.config.settings", autospec=True):
        settings.dex_wallet_address = account
        dex = DexSwap()
        result = await dex.get_trading_asset_balance()
        print(result)
        assert result is not None

@pytest.mark.asyncio
async def test_get_quote(account) -> str:
    """test token account."""
    with patch("dxsp.config.settings", autospec=True):
        settings.dex_wallet_address = account
        dex = DexSwap()
        result = await dex.get_quote('WBTC')
        print(result)
        assert result is not None

@pytest.mark.asyncio
async def test_get_decimals(account) -> str:
    """test token account."""
    with patch("dxsp.config.settings", autospec=True):
        settings.dex_wallet_address = account
        dex = DexSwap()
        result = await dex.get_token_decimals(settings.trading_asset_address)
        print(result)
        assert result is not None

# @pytest.mark.asyncio
# async def test_get_swap(account) -> str:
#     """test token account."""
#     with patch("dxsp.config.settings", autospec=True):
#         settings.dex_wallet_address = account
#         dex = DexSwap()
#         swap = await dex.get_swap('USDT','wBTC',quantity=10)
#         print(swap)
#         assert swap is not None