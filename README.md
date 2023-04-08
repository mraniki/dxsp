# swapportunity
a Defi Swap Helper package

![Pypi](https://img.shields.io/pypi/dm/swaportunity)

# Install
`pip install swapportunity`

2 swap execution mode are supported:
 - Single SWAP via 1inch API v5 and Uniswap version 2 router
 - Limit SWAP via 1inch API v3

# Example

[example](examples/example.py)
```
import os
from dotenv import load_dotenv
import asyncio
from web3 import Web3
import many_abis as ma

#YOUR VARIABLES
load_dotenv()
chain_id = os.getenv("CHAIN_ID", "10")
wallet_address = os.getenv("WALLET_ADDRESS", "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
private_key = os.getenv("PRIVATE_KEY", "0x111111111117dc0aa78b770fa6a738034120c302")
execution_mode = os.getenv("EXECUTION_MODE", "1")
#DERIVE DATA from MANY_ABIS FOR RPC and EXCHANGE
CHAIN = ma.get_chain_by_id(chain_id=int(chain_id))
NETWORK_PROVIDER_URL = os.getenv("NETWORK_PROVIDER_URL", CHAIN['rpc'][0])
dex_exchange = os.getenv("DEX_EXCHANGE", CHAIN['dex'][0])
#DEX CONNECTIVITY
w3 = Web3(Web3.HTTPProvider(NETWORK_PROVIDER_URL))


from swapportunity import DexSwap


async def main():
	#SWAP HELPER
	dex = DexSwap(w3,chain_id,wallet_address,private_key,execution_mode,dex_exchange)

	#INPUT for QUOTE
	quote = await dex.get_quote('ETH')
	print("quote ", quote)

	#INPUT for a NORMAL SWAP
	# transaction_amount_out = 10
	# asset_out_symbol = "USDT"
	# asset_in_symbol = "ETH"

	# transaction = dex.get_swap(transaction_amount_out,asset_out_symbol,asset_in_symbol)
	# print("transaction ", transaction)


if __name__ == "__main__":
    asyncio.run(main())
```

# Real case

[TalktTrader, submit trading order to CEX & DEX with messaging platform (Telegram, Matrix and Discord)](https://github.com/mraniki/tt)



# Roadmap

## V1
	- Single SWAP via 1inch API v5 and Uniswap version 2 router
 	- Limit SWAP via 1inch API v3

## V2 
	- Uniswap V3 Support
	- Ox or other API based swap platfrom
