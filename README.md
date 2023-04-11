# dxsp
DXSP (DeX SwaP), A defi swap helper package. 
Easy peasy Swap.

![Pypi](https://img.shields.io/pypi/dm/dxsp)
![Version](https://img.shields.io/pypi/v/dxsp)

[![Web3](https://badgen.net/badge/icon/web3/black?icon=libraries&label)](https://github.com/ethereum/web3.py)

[![coingecko](https://badgen.net/badge/icon/coingecko/black?icon=libraries&label)](https://github.com/coingecko)


# Install
`pip install dxsp`

# How to use it
```
from dxsp import DexSwap

	#SWAP HELPER
	dex = DexSwap(chain_id=chain_id,wallet_address=wallet_address,private_key=private_key,block_explorer_api=block_explorer_api)
	print("dex ", dex)
	#BUY 10 USDC to SWAP with BITCOIN
	demo_tx = await dex.get_swap('USDT','wBTC',10)
	print("demo_tx ", demo_tx)

	#SWAP with your OWN defined exchange like Sushiswap on ARBITRUM 
	sushi_router = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'
	dex_sushi = DexSwap(chain_id=42161,wallet_address=wallet_address,private_key=private_key,block_explorer_api=block_explorer_api,dex_exchange=sushi_router,base_trading_symbol='USDT')
	print("dex_sushi ", dex_sushi)
	#Execute ORDER to buy 1% of your USDT balance on SUSHISWAP ARBITRUM and get BTC token
	demo_order = await dex_sushi.execute_order(direction = 'BUY',symbol = 'wBTC')
	print("demo_order ", demo_order)
```
# Features

	- 7 blockchains mainnet and testnet supported with default block explorer, RPC, Router (uniswap and pancakeswap) and protocol url (1inch and 0x)
	- Other blockchain can be supported by provided attributes value such as block_explorer_url,web3 object or rpc url and contract outer
	- 2 swap protocol type supported:
		- 1inch API v5
		- Uniswap version 2 router protocol type
	- Automatic translation of symbol to contract address via user defined tokenlist format and/or coingecko api 
	- Web3 connectivity supported if no object given

# Attributes

## chain_id
	refers to [blockchains](assets/blockchains.py) for the list of supported chains for mainnet and testnet
	High Level:
	- "1": "ethereum",
	- "56": "binance",
	- "42161": "arbitrum",
	- "137": "polygon",
	- "10": "optimism",
	- "250": "fantom",
	- "43114": "avalanche"

## wallet_address 
	Your wallet public address. Mandatory. example: 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE,

## private_key  
	Your private key. Mandatory. example 0x111111111117dc0aa78b770fa6a738034120c302,

## block_explorer_api
	your API key for the chain explorer used to track the status of a swap. Mandatory. Refers to [blockchains](assets/blockchains.py) for the explorer url

## w3
	optional. a Web3 object

## protocol_type
	Protocol to interact with the DEX. optional and default value is "1inch". Other accepted values "uniswap_v2", "1inch_limit","uniswap_v3","0x"
         
## dex_exchange
	optional. Contract of the router/factory of the dexexchnage to be used.
	Default value refers to [blockchains](assets/blockchains.py) per chains
	example: `sushi_router = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'`

## base_trading_symbol 
	optional and default value is symbol 'USDC'

## amount_trading_option
	optional default value is 1. use for execute_order function.
	- 1:buy or sell %p percentage DEFAULT OPTION
	- 2:sell all token in case of sell order for example

# .Env
## Mandatory
	- None

## Optional
	- TOKENLIST: URL of a standard token list following tokenlist.org format
	- TESTTOKENLIST: URL of a standard testnet token list following tokenlist.org format


# Example
	[example](examples/example.py)


# Real case

	[TalkyTrader, submit trading order to CEX & DEX with messaging platform (Telegram, Matrix and Discord)](https://github.com/mraniki/tt)

# Roadmap

## V1
	- 1inch API v5 (#1 default)
	- Uniswap version 2 router DEX type (#2)
	- Limit SWAP via 1inch API v3 (#3)

## V2 
	- Uniswap V3 Support
	- Ox or other API based swap or orderbook platfrom

## Questions? Want to help? 
	[![discord](https://badgen.net/badge/icon/discord/purple?icon=discord&label)](https://discord.gg/vegJQGrRRa)
	[![telegram](https://badgen.net/badge/icon/telegram?icon=telegram&label)](https://t.me/TTTalkyTraderChat/1)
