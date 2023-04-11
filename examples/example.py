import sys
sys.path.append('../')
import os
from dotenv import load_dotenv
import asyncio
from web3 import Web3

#YOUR VARIABLES
load_dotenv()
#chain ID being used refer to https://chainlist.org/
chain_id = os.getenv("CHAIN_ID", 10)

#your wallet details
wallet_address = os.getenv("WALLET_ADDRESS", "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
private_key = os.getenv("PRIVATE_KEY", "0x111111111117dc0aa78b770fa6a738034120c302")

#Block explorer API from ETHERSCAN TYPE EXPLORER
block_explorer_api = os.getenv("BLOCK_EXPLORER_API", "1X23Q4ACZ5T3KXG67WIAH7X8C510F1972TM")

#network_provider_url = os.getenv("NETWORK_PROVIDER_URL")
#DEX CONNECTIVITY
#w3 = Web3(Web3.HTTPProvider(network_provider_url))
#protocol_type = os.getenv("protocol_type", "uniswap_v2")
# dex_exchange = os.getenv("DEX_EXCHANGE", 'uniswap_v2')
# base_trading_symbol = os.getenv("BASE_TRADE_SYMBOL", 'USDT')
# amount_trading_option = os.getenv("AMOUNT_TRADING_OPTION", 1)

from dxsp import DexSwap

async def main():
	#SWAP HELPER
	dex = DexSwap(chain_id=chain_id,wallet_address=wallet_address,private_key=private_key,block_explorer_api=block_explorer_api)
	
	#BUY 10 USDC to SWAP with BITCOIN
	demo_tx = await dex.get_swap('USDC','wBTC',10)
	print("demo_tx ", demo_tx)

	#NORMAL SWAP
	# transaction_amount_out = 10
	# asset_out_symbol = "USDT"
	# asset_in_symbol = "ETH"
	#SWAP EXECUTION
	# transaction = await dex.get_swap(transaction_amount_out,asset_out_symbol,asset_in_symbol)
	# print("transaction ", transaction)
	
	#order
	demo_order = dex.execute_order(
				direction = BUY,
				symbol = wBTC,
				stoploss = 1000,
				takeprofit = 1000, 
				quantity =1,
				amount_trading_option=1)
	print("demo_order ", demo_order)
	
	
	#QUOTE
	quote = await dex.get_quote('wBTC')
	print("quote ", quote)
	
	
	#get Contract Address
	bitcoinaddress = await dex.search_contract('wBTC')
	print("bitcoinaddress ", bitcoinaddress)
	#bitcoinaddress  0x68f180fcCe6836688e9084f035309E29Bf0A2095

	#getABI
	bitcoinaddressABI = await dex.get_abi(bitcoinaddress)
	print(bitcoinaddressABI)

if __name__ == "__main__":
    asyncio.run(main())