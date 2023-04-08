import os
from dotenv import load_dotenv
from web3 import Web3
import many_abis as ma

from swapportunity import DexSwap

#YOUR VARIABLES
load_dotenv()
CHAIN_ID = os.getenv("CHAIN_ID", "10")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "0x111111111117dc0aa78b770fa6a738034120c302")
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "1inch")

#DERIVE DATA from MANY_ABIS
CHAIN = ma.get_chain_by_id(chain_id=int(CHAIN_ID))
NETWORK_PROVIDER_URL = os.getenv("NETWORK_PROVIDER_URL", CHAIN['rpc'][0])
DEX_EXCHANGE = os.getenv("DEX_EXCHANGE", CHAIN['dex'][0])

#DEX CONNECTIVITY
EXCHANGE = Web3(Web3.HTTPProvider(NETWORK_PROVIDER_URL))

#SWAP HELPER
dex = DexSwap(EXCHANGE,CHAIN_ID,WALLET_ADDRESS,PRIVATE_KEY,EXECUTION_MODE,DEX_EXCHANGE)

#INPUT for QUOTE
quote = dex.get_quote('ETH')
print(quote)


#INPUT for a NORMAL SWAP
	# transaction_amount_out = 10
	# asset_out_symbol = "USDT"
	# asset_in_symbol = "ETH"

	# transaction = dex.get_swap(transaction_amount_out,asset_out_symbol,asset_in_symbol)
	# print(transaction)


#INPUT for a  LIMIT SWAP
# TBD