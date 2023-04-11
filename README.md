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
