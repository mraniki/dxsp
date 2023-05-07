import pytest
from unittest.mock import MagicMock
from dxsp import DexSwap


@pytest.mark.asyncio
async def test_init_dex():
    """Init Testing"""
    exchange = DexSwap()
    check = "DexSwap" in str(type(exchange))
    assert check is True
    assert exchange.w3 is not None
    assert exchange.chain_id == 1
    assert exchange.protocol_type == "1inch"
    assert exchange.wallet_address == (
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
    assert exchange.private_key == "0x111111111117dc0aaaaaa0fa6a738034aaaa302"
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


@pytest.mark.asyncio
async def test_uniswap_v2_quote():
    # Mock the router instance
    router_instance = MagicMock()
    router_instance.functions.getAmountsOut.return_value.call.return_value = [0, 1234]

    exchange = DexSwap()

    # Call the function being tested
    result = await exchange.uniswap_v2_quote("asset_in_address", "asset_out_address", amount=1)

    # Check the result
    assert result == 1234


@pytest.mark.asyncio
async def test_oneinch_swap():
    # Mock the _get method
    exchange = DexSwap()
    exchange._get = MagicMock(return_value={"statusCode": 200})

    result = await exchange.oneinch_swap("asset_out_address", "asset_in_address", "100")

    assert result == {"statusCode": 200}


@pytest.mark.asyncio
async def test_get_confirmation():
    # Mock the required attributes and methods
    exchange = DexSwap()
    exchange.logger = MagicMock()
    exchange.w3.eth.get_transaction_receipt = MagicMock(return_value={"gasUsed": 100})
    exchange.w3.eth.get_block = MagicMock(return_value={"timestamp": 12345})
    order_hash_details = {"blockNumber": 123}
    asset_out_symbol = "ETH"
    asset_out_address = "0x123"
    order_amount = 1

    # Call the function being tested
    result = await exchange.get_confirmation(
    "order_hash",
    order_hash_details,
    asset_out_symbol,
    asset_out_address,
    order_amount)

    # Check the result
    assert "id" in result
    assert "timestamp" in result
    assert "instrument" in result
    assert "contract" in result
    assert "amount" in result
    assert "fee" in result
    assert "price" in result
    assert "confirmation" in result


@pytest.mark.asyncio
async def test_execute_order():
    exchange = DexSwap()
    # call the function and check the output
    order_params = {"action": "BUY", "instrument": "ETH", "quantity": 1}
    result = await exchange.execute_order(order_params)
    assert isinstance(result, str)
    
    