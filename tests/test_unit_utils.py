"""
 DEXclient Unit Test
"""

from unittest.mock import MagicMock

import pytest
from web3 import Web3

from dxsp import DexSwap
from dxsp.config import settings
from dxsp.utils.utils import fetch_url


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="dxsp")


@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


@pytest.fixture(name="dex_client")
def client_fixture(dex):
    for dx in dex.clients:
        if dx.protocol == "uniswap":
            return dx


@pytest.fixture(name="mock_w3")
def mock_w3_fixture():
    mock = MagicMock(spec=Web3)
    mock.is_connected.return_value = True
    mock.eth = MagicMock()
    mock.eth.block_number = 100
    mock.to_checksum_address = Web3.to_checksum_address
    return mock


### UTILS CONTRACT
# @pytest.mark.asyncio
# async def test_get_cg_data(dex_client):
#     result = await dex_client.get_quote(sell_symbol="LINK")
#     assert result is not None
#     assert isinstance(result, float)


# @pytest.mark.asyncio
# async def test_get_token_exception(dex_client, caplog):
#     await dex_client.get_quote(sell_symbol="NOTATHING")
#     assert "Quote failed" in caplog.text


@pytest.mark.asyncio
async def test_get_confirmation(dex_client):
    result = await dex_client.contract_utils.get_confirmation(
        "0xea5a0fd0a15f68ef2f4b38661d445aa14de06a88844adc236bb071c46734fd09"
    )
    print(result)
    assert result is not None
    assert result["timestamp"] is not None
    assert result["fee"] is not None
    assert result["confirmation"] is not None
    assert "➕" in result["confirmation"]
    assert "⛽" in result["confirmation"]
    assert "🗓️" in result["confirmation"]
    assert "ℹ️" in result["confirmation"]


### UTILS ACCOUNT


@pytest.mark.asyncio
async def test_get_approve(dex_client):
    symbol = "UNI"
    approve_receipt = None
    try:
        approve_receipt = await dex_client.account.get_approve(symbol)
        print(approve_receipt)
    except Exception as e:
        print(f"Error getting approve receipt: {e}")
    assert approve_receipt is None


@pytest.mark.asyncio
async def test_get_gas(dex_client):
    """get_gas Testing"""
    mock_tx = {
        "to": "0x5f65f7b609678448494De4C87521CdF6cEf1e932",
        "value": "1000000000000000000",
    }
    result = await dex_client.account.get_gas(mock_tx)
    print(result)
    assert result is not None


@pytest.mark.asyncio
async def test_get_gas_price(dex_client):
    result = await dex_client.account.get_gas_price()
    print(f"gas_price: {result}")
    assert result is not None


@pytest.mark.asyncio
async def test_fetch_url_error():
    url = ""
    response = await fetch_url(url)
    assert response is None


@pytest.mark.asyncio
async def test_fetch_url_large_response(caplog):
    url = "https://github.com/seductiveapps/largeJSON/raw/master/100mb.json"
    response = await fetch_url(url)
    assert response is None
    assert "Response content is too large to process." in caplog.text


# ### UTILS WALLET MONITOR

# MONITORED_ADDRESS = "0x1234567890123456789012345678901234567890"
# OTHER_ADDRESS = "0x0987654321098765432109876543210987654321"

# @pytest.mark.asyncio
# async def test_wallet_monitor_init_success(mock_w3):
#     monitor = WalletMonitor(w3=mock_w3, address_to_monitor=MONITORED_ADDRESS)
#     assert monitor.w3 == mock_w3
#     assert monitor.address_to_monitor == Web3.to_checksum_address(MONITORED_ADDRESS)
#     assert monitor.polling_interval == 15

# @pytest.mark.asyncio
# async def test_wallet_monitor_init_custom_interval(mock_w3):
#     monitor = WalletMonitor(
#         w3=mock_w3,
#         address_to_monitor=MONITORED_ADDRESS,
#         polling_interval=5
#     )
#     assert monitor.polling_interval == 5

# @pytest.mark.asyncio
# async def test_wallet_monitor_init_invalid_address(mock_w3):
#     with pytest.raises(ValueError, match="Invalid Ethereum address format"):
#         WalletMonitor(w3=mock_w3, address_to_monitor="invalid-address")

# @pytest.mark.asyncio
# async def test_wallet_monitor_init_disconnected_w3(mock_w3):
#     mock_w3.is_connected.return_value = False
#     with pytest.raises(ValueError, match="Invalid Web3 instance provided"):
#         WalletMonitor(w3=mock_w3, address_to_monitor=MONITORED_ADDRESS)

# # Test the start_monitoring generator
# @pytest.mark.asyncio
# @patch("asyncio.sleep", return_value=None) # Mock sleep to avoid delays
# async def test_wallet_monitor_start_monitoring(mock_sleep, mock_w3):
#     # --- Setup Mock Transactions and Blocks ---
#     tx1_data = {
#         'hash': b'\x01'*32,
#         'from': MONITORED_ADDRESS,
#         'to': OTHER_ADDRESS,
#         'input': '0x',
#         'value': 100
#     }
#     tx2_data = {
#         'hash': b'\x02'*32,
#         'from': OTHER_ADDRESS, # Different sender
#         'to': MONITORED_ADDRESS,
#         'input': '0x',
#         'value': 200
#     }
#     tx3_data = {
#         'hash': b'\x03'*32,
#         'from': MONITORED_ADDRESS, # Monitored sender again
#         'to': OTHER_ADDRESS,
#         'input': '0xabc',
#         'value': 300
#     }

#     # Use AttributeDict to mimic web3 transaction structure
#     tx1 = AttributeDict(tx1_data)
#     tx2 = AttributeDict(tx2_data)
#     tx3 = AttributeDict(tx3_data)

#     block101_data = {'number': 101, 'transactions': [tx1, tx2]}
#     block102_data = {'number': 102, 'transactions': [tx3]}
#     block103_data = {'number': 103, 'transactions': []} # Empty block

#     block101 = AttributeDict(block101_data)
#     block102 = AttributeDict(block102_data)
#     block103 = AttributeDict(block103_data)

#     # --- Configure Mock Web3 ---
#     # Simulate block number increase
#     block_num_sequence = [100, 101, 102, 103, 103] # Stays at 103 after last block
#     mock_w3.eth.block_number = MagicMock(side_effect=block_num_sequence)

#     # Mock get_block responses
#     def mock_get_block(block_identifier, full_transactions=False):
#         if block_identifier == 101 and full_transactions:
#             return block101
#         if block_identifier == 102 and full_transactions:
#             return block102
#         if block_identifier == 103 and full_transactions:
#             return block103
#         return None # Should not happen in this test

#     mock_w3.eth.get_block = MagicMock(side_effect=mock_get_block)

#     # --- Run Monitor ---
#     monitor = WalletMonitor(
#         w3=mock_w3,
#         address_to_monitor=MONITORED_ADDRESS,
#         polling_interval=1
#     )
#     yielded_transactions = []
#     iterations = 0
#     MAX_ITERATIONS = 5 # Prevent infinite loop if logic is wrong

#     async for tx in monitor.start_monitoring():
#         yielded_transactions.append(tx)
#         iterations += 1
#         if iterations >= MAX_ITERATIONS:
#             break

#     # --- Assertions ---
#     assert len(yielded_transactions) == 2 # tx1 and tx3 should be yielded
#     assert yielded_transactions[0]['hash'] == tx1['hash']
#     assert yielded_transactions[1]['hash'] == tx3['hash']
#     assert mock_w3.eth.get_block.call_count >= 3 # Called for 101, 102, 103
#     # Check if called with full_transactions=True
#     mock_w3.eth.get_block.assert_any_call(101, full_transactions=True)
#     mock_w3.eth.get_block.assert_any_call(102, full_transactions=True)
#     mock_w3.eth.get_block.assert_any_call(103, full_transactions=True)
#     assert mock_sleep.call_count > 0 # Ensure the loop waited


# ### UTILS UTILS
