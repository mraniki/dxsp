# """
#  DEXSWAP Unit Test
# """
# from unittest.mock import AsyncMock, patch

# import pytest
# from web3 import EthereumTesterProvider, Web3

# from dxsp import DexTrader
# from dxsp.config import settings


# @pytest.fixture(scope="session", autouse=True)
# def set_test_settings():
#     settings.configure(FORCE_ENV_FOR_DYNACONF="uniswap")


# @pytest.fixture(name="dextrader")
# def DexTrader_fixture():
#     return DexTrader()


# @pytest.fixture(name="dex")
# def DexClient_fixture(dextrader):
#     for dx in dextrader.dex_info:
#         yield dx.client


# @pytest.fixture
# def tester_provider():
#     return EthereumTesterProvider()


# @pytest.fixture(name="web3")
# def w3():
#     provider = EthereumTesterProvider()
#     return Web3(provider)


# @pytest.fixture(name="account")
# def account_fixture(web3) -> str:
#     """setup account."""
#     return web3.eth.accounts[0]


# @pytest.fixture(name="order")
# def order_params_fixture():
#     """Return order parameters."""
#     return {
#         'action': 'BUY',
#         'instrument': 'WBTC',
#         'quantity': 1,
#     }


# @pytest.fixture(name="invalid_order")
# def invalid_order_fixture():
#     """Return order parameters."""
#     return {
#         'action': 'BUY',
#         'instrument': 'NOTATHING',
#         'quantity': 1,
#     }


# @pytest.fixture(name="test_contract")
# def mock_contract(dex):
#     contract = AsyncMock()
#     contract.get_token_decimals.return_value = 18
#     contract.to_wei.return_value = 1000000000000000000
#     contract.functions.balanceOf = AsyncMock(return_value=100)
#     contract.wait_for_transaction_receipt.return_value = {"status": 1}
#     return contract



# def test_dynaconf_is_in_testing():
#     print(settings.VALUE)
#     assert settings.VALUE == "On Testing"

# @pytest.mark.asyncio
# async def test_get_info(dex):
#     result = await dex.get_info()
#     print(result)
#     assert result is not None


# @pytest.mark.asyncio
# async def test_get_name(dex):
#     result = await dex.get_name()
#     assert isinstance(result, str)
#     assert len(result) == 8


# @pytest.mark.asyncio
# async def test_get_account_balance(dex):
#     # Call the get_account_balance method
#     result = await dex.get_account_balance()
#     assert result is not None
#     assert '₿' in result


# @pytest.mark.asyncio
# async def test_account_balance(account) -> str:
#     """test balance account."""
#     with patch("dxsp.config.settings", autospec=True):
#         settings.dex_wallet_address = account
#         print(settings.dex_wallet_address)
#         dex = DexTrader()
#         print(dex.account.wallet_address)
#         result = await dex.get_account_balance()
#         print(result)
#         assert result is not None
#         assert '₿' in result
#         assert '💵' in result


# @pytest.mark.asyncio
# async def test_trading_asset_balance(account) -> str:
#     """test token account."""
#     with patch("dxsp.config.settings", autospec=True):
#         settings.dex_wallet_address = account
#         dex = DexTrader()
#         result = await dex.get_trading_asset_balance()
#         print(result)
#         assert result is not None


# @pytest.mark.asyncio
# async def test_get_account_position(account) -> str:
#     """test token account."""
#     with patch("dxsp.config.settings", autospec=True):
#         settings.dex_wallet_address = account
#         # with pytest.raises(ValueError, match='No Balance'):
#         dex = DexTrader()
#         result = await dex.get_account_position()
#         print(result)
#         assert result is not None
#         assert '📊' in result


# @pytest.mark.asyncio
# async def test_get_account_transactions(dex):
#     # Call the get_account_transactions method
#     result = await dex.get_account_transactions()
#     print(f"history: {result}")
#     assert result is not None
#     assert 'pnl' in result
#     assert 'tokenList' in result


# @pytest.mark.asyncio
# async def test_get_account_pnl(dex):
#     # Call the get_account_pnl method
#     result = await dex.get_account_pnl()
#     print(f"pnl: {result}")
#     assert result is not None
#     assert 'Total' in result
#     assert '📊' in result
#     assert 'Opened' in result
#     assert 'Margin' in result

# @pytest.mark.asyncio
# async def test_get_approve(dex):
#     symbol = "UNI"
#     approve_receipt = None
#     try:
#         approve_receipt = await dex.get_approve(symbol)
#         print(approve_receipt)
#     except Exception as e:
#         print(f"Error getting approve receipt: {e}")
#     assert approve_receipt is None


# @pytest.mark.asyncio
# async def test_failed_get_approve(dex):
#     with pytest.raises(ValueError, match='Approval failed'):
#         await dex.account.get_approve("0xdAC17F958D2ee523a2206206994597C13D831ec7")


# @pytest.mark.asyncio
# async def test_get_sign():
#     pass



# @pytest.mark.asyncio
# async def test_get_gas(dex):
#     """get_gas Testing"""
#     mock_tx = {"to": "0x1234567890123456789012345678901234567890",
#                 "value": "1000000000000000000"}
#     result = await dex.account.get_gas(mock_tx)
#     print(result)


# @pytest.mark.asyncio
# async def test_get_gas_price(dex):
#     # Call the get_gasPrice method
#     result = await dex.account.get_gas_price()
#     print(f"gas_price: {result}")
#     assert result is not None