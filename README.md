# DXSP (DeX SwaP)


|<img width="200" alt="Logo" src="https://user-images.githubusercontent.com/8766259/231213427-63ea2752-13d5-4993-aee2-90671b57fc6e.png">  | A python defi swap helper package. Swap made easy. |
| ------------- | ------------- |
|[![Pypi](https://badgen.net/badge/icon/dxsp?icon=pypi&label)](https://pypi.org/project/dxsp/) ![Version](https://img.shields.io/pypi/v/dxsp)<br>  ![Pypi](https://img.shields.io/pypi/dm/dxsp) [![Docker Pulls](https://badgen.net/docker/pulls/mraniki/dxsp)](https://hub.docker.com/r/mraniki/dxsp)<br>[![✨Flow](https://github.com/mraniki/dxsp/actions/workflows/%E2%9C%A8Flow.yml/badge.svg)](https://github.com/mraniki/dxsp/actions/workflows/%E2%9C%A8Flow.yml) [![codecov](https://codecov.io/gh/mraniki/dxsp/branch/main/graph/badge.svg?token=39ED0ZA6IH)](https://codecov.io/gh/mraniki/dxsp) <br>![](https://healthchecks.io/badge/227be4cc-702a-4ac8-b37b-d3d5a3/UcTrNrys-2/dxsp.svg)<br>[![Web3](https://badgen.net/badge/icon/web3/black?icon=libraries&label)](https://github.com/ethereum/web3.py) [![coingecko](https://badgen.net/badge/icon/coingecko/black?icon=libraries&label)](https://github.com/coingecko)|24 blockchains (ETH, BSC, ARB, MATIC, OPT...)<br>2 swap protocol (1inch API, UniV2 router)



Key features:

- 24 blockchains mainnet and testnet supported with default block explorer, RPC, Router (uniswap and pancakeswap) and protocol url (1inch and 0x). Other blockchains can be supported via function attributes
- 2 swap protocol type supported:
	- 1inch API v5
	- Uniswap version 2 router protocol type

Other features:
- Translate token symbol to contract address via user defined tokenlist format or coingecko api 
- Connect to web3  if no web3 object or no rpc provided
- Able to approve contract and sign transaction
- Quote for a given token
- Use Base symbol like stablecoin



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
## Example
[example](https://github.com/mraniki/dxsp/blob/main/examples/example.py)

## Real use case
[TalkyTrader, submit trading order to CEX & DEX with messaging platform (Telegram, Matrix and Discord)](https://github.com/mraniki/tt)


# Documentation
https://github.com/mraniki/dxsp/wiki

## 🚧 Roadmap

[🚧 Roadmap](https://github.com/mraniki/dxsp/milestones)

## Questions? Want to help? 
[![discord](https://badgen.net/badge/icon/discord/purple?icon=discord&label)](https://discord.gg/vegJQGrRRa)
[![telegram](https://badgen.net/badge/icon/telegram?icon=telegram&label)](https://t.me/TTTalkyTraderChat/1)
