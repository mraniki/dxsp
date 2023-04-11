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
	dex = DexSwap(chain_id=10,wallet_address='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',private_key='0x111111111117dc0aa78b770fa6a738034120c302',block_explorer_api='1X23Q4ACZ5T3KXG67WIAH7X8C510F1972TM')
	swap = await dex.get_swap('USDC','wBTC',10)
```
# Features

2 swap protocol mode are supported:
 - 1inch API v5
 - Uniswap version 2 router protocol type

Limit SWAP via 1inch API v3 and Uniswap version to be done

# Attributes

## chain_id
 refers to [blockchains](assets/blockchains.py) for the list of supported chains
          "1": "ethereum",
          "56": "binance",
          "42161": "arbitrum",
          "137": "polygon",
          "10": "optimism",
          "250": "fantom",
          "43114": "avalanche"

## wallet_address 

public address
example: 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE,
## private_key  

example 0x111111111117dc0aa78b770fa6a738034120c302,

## block_explorer_api
API for the chain explorer used to track the status of a swap.
refers to [blockchains](assets/blockchains.py) for the explorer url

## w3
 Web3 object

## protocol_type

protocol to interact with the DEX
optional and default value is "1inch". 
other accepted values "uniswap_v2", "1inch_limit","uniswap_v3","0x"
         
## dex_exchange

optional default value refers to [blockchains](assets/blockchains.py) for the list of supported chains

## base_trading_symbol 

optional and default value is symbol 'USDC'

## amount_trading_option

optional default value is 1. use for execute_order function.

- 1:buy or sell %p percentage DEFAULT OPTION
- 2:SELL all token in case of sell order for example

# .Env
Mandatory
 - None

Optional
 - TOKENLIST: URL of a standard token list following tokenlist.org format
 - TESTTOKENLIST: URL of a standard testnet token list following tokenlist.org format


# Example

## SHORT

### Swap 10 USDC for BITCOIN on OPT chain:

```
	from dxsp import DexSwap
	dex = DexSwap(chain_id=10,wallet_address='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',private_key='0x111111111117dc0aa78b770fa6a738034120c302',block_explorer_api='1X23Q4ACZ5T3KXG67WIAH7X8C510F1972TM')
	swap = await dex.get_swap('USDC','wBTC',10)
```

## LONG
[example](examples/example.py)
```diff
	DexSwap details
```

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
