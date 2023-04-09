# dxsp
DXSP (DeX SwaP), A defi swap helper package. 
Easy peasy Swap.

![Pypi](https://img.shields.io/pypi/dm/dxsp)
![Version](https://img.shields.io/pypi/v/dxsp)

# Install
`pip install dxsp`

# How to use it
```
from dxsp import DexSwap
dex = DexSwap(w3,chain_id,wallet_address,private_key,protocol,dex_exchange,block_explorer_api)
tx = await dex.get_swap(10,'USDC','wBTC')
print(tx)
```

2 swap protocol mode are supported:
 - 1inch API v5 (#1 default)
 - Uniswap version 2 router DEX type (#2)

Limit SWAP via 1inch API v3 and Uniswap version to be done

# .Env
Mandatory
 - None

Optional
 - TOKENLIST: URL of a standard token list following tokenlist.org format
 - TESTTOKENLIST: URL of a standard testnet token list following tokenlist.org format

# Example

[example](examples/example.py)
```diff
import os
from dotenv import load_dotenv
import asyncio
from web3 import Web3
import many_abis as ma

#YOUR VARIABLES
load_dotenv()
#chain ID being used refer to https://chainlist.org/
chain_id = os.getenv("CHAIN_ID", 10)

#your wallet details
wallet_address = os.getenv("WALLET_ADDRESS", "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
private_key = os.getenv("PRIVATE_KEY", "0x111111111117dc0aa78b770fa6a738034120c302")

#1 for 1inch and 2 for Uniswap V2
protocol = os.getenv("PROTOCOL", "1")

#DATA from MANY_ABIS FOR RPC and EXCHANGE
chain = ma.get_chain_by_id(chain_id=int(chain_id))
network_provider_url = os.getenv("NETWORK_PROVIDER_URL", chain['rpc'][0])
dex_exchange = os.getenv("DEX_EXCHANGE", chain['dex'][0])

#Block explorer API from ETHERSCAN TYPE EXPLORER
block_explorer_api = os.getenv("BLOCK_EXPLORER_API", "1X23Q4ACZ5T3KXG67WIAH7X8C510F1972TM")

#DEX CONNECTIVITY
w3 = Web3(Web3.HTTPProvider(network_provider_url))


+from dxsp import DexSwap

async def main():
	#SWAP HELPER
+	dex = DexSwap(w3,chain_id,wallet_address,private_key,protocol,dex_exchange,block_explorer_api)
	#DEMO SWAP
+	demo_tx = await dex.get_swap(10,'USDC','wBTC')
	print("demo_tx ", demo_tx)

	#QUOTE
	quote = await dex.get_quote('wBTC')
	print("quote ", quote)

	#NORMAL SWAP
	transaction_amount_out = 10
	asset_out_symbol = "USDT"
	asset_in_symbol = "ETH"
	#SWAP EXECUTION
	transaction = await dex.get_swap(transaction_amount_out,asset_out_symbol,asset_in_symbol)
	print("transaction ", transaction)
	
	#get Contract Address
	bitcoinaddress = await dex.search_contract('wBTC')
	print("bitcoinaddress ", bitcoinaddress)
	#bitcoinaddress  0x68f180fcCe6836688e9084f035309E29Bf0A2095
	# check : https://optimistic.etherscan.io/token/0x68f180fcce6836688e9084f035309e29bf0a2095?a=0x5bb949b4938aaf1b2e97f4871a8968a4abea7c98

	#getABI
	# bitcoinABI = await dex.get_abi(bitcoinaddress)
	# print("bitcoinABI ", bitcoinABI)


if __name__ == "__main__":
    asyncio.run(main())
```

# Real case

[TalkyTrader, submit trading order to CEX & DEX with messaging platform (Telegram, Matrix and Discord)](https://github.com/mraniki/tt)

# Roadmap

## V1
	- Single SWAP via 1inch API v5 and Uniswap version 2 router
	- Limit SWAP via 1inch API v3

## V2 
	- Uniswap V3 Support
	- Ox or other API based swap or orderbook platfrom
