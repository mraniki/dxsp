import pytest
from web3 import Web3
from unittest.mock import MagicMock, patch
from dxsp import DexSwap


@pytest.fixture
def web3():
    # create a mock web3 instance
    return Web3(Web3.EthereumTesterProvider())


@pytest.fixture
def asset_in_address():
    # create a mock asset in address
    return "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984" # UNI token address


@pytest.fixture
def asset_out_address():
    # create a mock asset out address
    return "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2" # WETH token address


@pytest.fixture
def router(web3):
    # create a mock router contract
    return web3.eth.contract(abi=..., address=...)


@pytest.fixture
def token_contract(web3):
    # create a mock token contract
    return web3.eth.contract(abi=..., address=...)


@pytest.fixture
def swap_contract(web3):
    # create a mock swap contract
    return web3.eth.contract(abi=..., address=...)

@pytest.mark.asyncio
async def test_init_dex():
    """Init Testing"""
    exchange = DexSwap()
    check = "DexSwap" in str(type(exchange))
    assert check is True
    assert exchange.w3 is not None
    assert exchange.chain_id is not None
    assert exchange.protocol_type  is not None
    assert exchange.wallet_address.startswith("0x")
    assert exchange.private_key.startswith("0x")
    assert exchange.cg_platform is not None


@pytest.mark.asyncio
async def test_get_quote():
    """getquote Testing"""
    exchange = DexSwap()
    quote = await exchange.get_quote("WBTC")
    if quote:
        assert quote is not None


@pytest.mark.asyncio
async def test_search_contract():
    """search_contract Testing"""
    exchange = DexSwap()
    contract = await exchange.search_contract("WBTC")
    if contract:
        assert contract is not None
        assert contract == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"


@pytest.mark.asyncio
async def test_get_contract_address():
    """get_contract_address Testing"""
    exchange = DexSwap()
    token_mainnet_list = (
        "https://raw.githubusercontent.com/mraniki/tokenlist/main/all.json")
    address = await exchange.get_contract_address(token_mainnet_list, "WBTC")
    if address:
        print(address)
        assert address is not None
        assert address == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"


@pytest.mark.asyncio
async def test_get_token_contract():
    """get_token_contract Testing"""
    exchange = DexSwap()
    contract = await exchange.get_token_contract("WBTC")
    if contract:
        assert contract is not None
        assert type(contract) is exchange.w3.eth.contract


@pytest.mark.asyncio
async def test_router():
    """router Testing"""
    exchange = DexSwap()
    router = await exchange.router()
    if router:
        assert router is not None


@pytest.mark.asyncio
async def test_logger(caplog):
    exchange = DexSwap()
    for record in caplog.records:
        assert record.levelname != "CRITICAL"
        assert "wally" not in caplog.text


@pytest.fixture
def oneinch_quote():
    # create the function to be tested
    async def oneinch_quote(
        self,
        asset_in_address,
        asset_out_address,
        amount=1
    ):
        asset_out_amount = 1000000000000000000
        quote_url = (
            "https://api.1inch.exchange/v5.0/1"
            + "/quote?fromTokenAddress="
            + str(asset_in_address)
            + "&toTokenAddress="
            + str(asset_out_address)
            + "&amount="
            + str(asset_out_amount))
        quote_response = await self._get(quote_url)
        self.logger.debug("quote %s", quote_response)
        quote_amount = quote_response['toTokenAmount']
        quote_decimals = quote_response['fromToken']['decimals']


    
    return oneinch_quote

# @patch("oneinch_quote._get")
# def test_oneinch_quote_success(
#     mock_get,
#     asset_in_address,
#     asset_out_address,
#     oneinch_quote
#      ):
#     # test that the function returns a valid quote when successful
#     amount = 100  # swap 100 UNI tokens for WETH tokens
#     mock_get.return_value = {
#         "fromToken": {
#             "decimals": 18,
#             "symbol": "UNI"
#         },
#         "toToken": {
#             "decimals": 18,
#             "symbol": "WETH"
#         },
#         "toTokenAmount": "1234567890000000000"  # 1.23456789 WETH tokens
#     }
#     quote = oneinch_quote(asset_in_address, asset_out_address, amount)
#     assert quote == 0.01  # the quote should be 0.01 WETH per UNI


# @patch("oneinch_quote._get")
# def test_oneinch_quote_failure(
#     mock_get,
#     web3,
#     asset_in_address,
#     asset_out_address,
#     oneinch_quote
#      ):
#     # test that the function raises an exception when failed
#     amount = 100  # swap 100 UNI tokens for WETH tokens
#     mock_get.return_value = {
#         "error": "Invalid token address"
#     }
#     with pytest.raises(Exception):
#         quote = oneinch_quote(asset_in_address, asset_out_address, amount)


# @pytest.fixture
# def uniswap_v2_quote(web3, router):
#     # create the function to be tested
#     async def uniswap_v2_quote(
#         self,
#         asset_in_address,
#         asset_out_address,
#         amount=1
#     ):
#         order_path_dex = [asset_out_address, asset_in_address]
#         router_instance = await self.router()
#         order_min_amount = int(
#             router_instance.functions.getAmountsOut(
#                 amount,
#                 order_path_dex)
#             .call()[1])
#         return order_min_amount

#     return uniswap_v2_quote


# def test_uniswap_v2_quote_success(
#     web3,
#     asset_in_address,
#     asset_out_address,
#     uniswap_v2_quote
#      ):
#     # test that the function returns a valid amount when successful
#     amount = 100  # swap 100 UNI tokens for WETH tokens
#     min_amount = uniswap_v2_quote(asset_in_address, asset_out_address, amount)
#     assert min_amount > 0  # the minimum amount should be positive


# def test_uniswap_v2_quote_failure(
#     web3,
#     asset_in_address,
#     asset_out_address,
#     uniswap_v2_quote
#      ):
#     # test that the function raises an exception when failed
#     amount = 0 # swap 0 UNI tokens for WETH tokens
#     with pytest.raises(Exception):
#         min_amount = uniswap_v2_quote(
#             asset_in_address,
#             asset_out_address,
#             amount)


# # @pytest.mark.asyncio
# # async def test_oneinch_swap():
# #     # Mock the _get method
# #     exchange = DexSwap()
# #     exchange._get = MagicMock(return_value={"statusCode": 200})

# #     result = await exchange.oneinch_swap(
# #         "asset_out_address", 
# #         "asset_in_address", 
# #         "100")

# #     assert result == {"statusCode": 200}


# # @pytest.mark.asyncio
# # async def test_get_confirmation():
# #     # Mock the required attributes and methods
# #     exchange = DexSwap()
# #     exchange.logger = MagicMock()
# #     exchange.w3.eth.get_transaction_receipt = MagicMock(return_value={"gasUsed": 100})
# #     exchange.w3.eth.get_block = MagicMock(return_value={"timestamp": 12345})
# #     order_hash_details = {"blockNumber": 123}
# #     asset_out_symbol = "ETH"
# #     asset_out_address = "0x123"
# #     order_amount = 1

# #     # Call the function being tested
# #     result = await exchange.get_confirmation(
# #         "order_hash",
# #         order_hash_details,
# #         asset_out_symbol,
# #         asset_out_address,
# #         order_amount)

# #     # Check the result
# #     assert "id" in result
# #     assert "timestamp" in result
# #     assert "instrument" in result
# #     assert "contract" in result
# #     assert "amount" in result
# #     assert "fee" in result
# #     assert "price" in result
# #     assert "confirmation" in result



# @pytest.fixture
# def order_params():
#     # create some sample order parameters
#     return {
#         "action": "BUY",
#         "instrument": "ETH",
#         "quantity": 10
#     }


# @pytest.fixture
# def execute_order(web3, token_contract, swap_contract):
#     # create the function to be tested
#     async def execute_order(self, order_params):
#         """execute swap function"""
#         action = order_params.get('action')
#         instrument = order_params.get('instrument')
#         quantity = order_params.get('quantity', 1)

#         try:
#             asset_out_symbol = ("USDT" if
#                                 action == "BUY" else instrument)
#             asset_in_symbol = (instrument if action == "BUY"
#                                else "USDT")
#             asset_out_contract = await self.get_token_contract(
#                 asset_out_symbol)
#             try:
#                 asset_out_decimals = (
#                     asset_out_contract.functions.decimals().call())
#             except Exception as e:
#                 self.logger.error("execute_order decimals: %s", e)
#                 asset_out_decimals = 18
#             asset_out_balance = await self.get_token_balance(asset_out_symbol)
#             #  buy or sell %p percentage DEFAULT OPTION is 10%
#             asset_out_amount = ((asset_out_balance) /
#                                 (10
#                                 ** asset_out_decimals)
#                                 )*(float(quantity)/100)

#             order = await self.get_swap(
#                     asset_out_symbol,
#                     asset_in_symbol,
#                     asset_out_amount
#                     )
#             if order:
#                 return order['confirmation']

#         except Exception as e:
#             self.logger.debug("error execute_order %s", e)
#             return "error processing order in DXSP"

#     return execute_order


# def test_execute_order_success(web3, order_params, execute_order):
#     # test that the function returns a confirmation when successful
#     confirmation = execute_order(order_params)
#     assert confirmation.startswith("0x")


# def test_execute_order_failure(web3, order_params, execute_order):
#     # test that the function returns an error message when failed
#     order_params["action"] = "INVALID" # make the order invalid
#     error_message = execute_order(order_params)
#     assert error_message == "error processing order in DXSP"
