# DXSP (DeX SwaP)

|<img width="200" alt="Logo" src="https://user-images.githubusercontent.com/8766259/231213427-63ea2752-13d5-4993-aee2-90671b57fc6e.png">  | A python defi swap helper package. Swap made easy |
| ------------- | ------------- |
|[![wiki](https://img.shields.io/badge/🪙🗿-wiki-0080ff)](https://talkytrader.gitbook.io/talky/) [![Pypi](https://badgen.net/badge/icon/dxsp?icon=pypi&label)](https://pypi.org/project/dxsp/) ![Version](https://img.shields.io/pypi/v/dxsp)<br>  ![Pypi](https://img.shields.io/pypi/dm/dxsp) [![Docker Pulls](https://badgen.net/docker/pulls/mraniki/dxsp)](https://hub.docker.com/r/mraniki/dxsp)<br> [![✨Flow](https://github.com/mraniki/dxsp/actions/workflows/%E2%9C%A8Flow.yml/badge.svg)](https://github.com/mraniki/dxsp/actions/workflows/%E2%9C%A8Flow.yml) [![codecov](https://codecov.io/gh/mraniki/dxsp/branch/main/graph/badge.svg?token=39ED0ZA6IH)](https://codecov.io/gh/mraniki/dxsp) <br>![](https://healthchecks.io/badge/227be4cc-702a-4ac8-b37b-d3d5a3/UcTrNrys-2/dxsp.svg)<br>[![Web3](https://badgen.net/badge/icon/web3/black?icon=libraries&label)](https://github.com/ethereum/web3.py) [![coingecko](https://badgen.net/badge/icon/coingecko/black?icon=libraries&label)](https://github.com/coingecko)|Key blockchains (ETH, BSC, ARB, MATIC, OPT...)<br>Key swap protocol (UniV2 router)

Key features:

- Any blockchains mainnet or testnet supported by web3py, 1inch or uniswap type router.


Other features:

- Translate token symbol to contract address via user defined tokenlist format or coingecko api
- Connect to web3 automatically (optionn to provide a web3 object)
- Approve contract and sign transaction
- Quote a given token
- Use Base trading symbol like stablecoin
- Settings to use the module for your own setup

## Install

`pip install dxsp`

## How to use it

```
from dxsp import DexSwap

 dex = DexSwap()
 #BUY 10 USDC to SWAP with BITCOIN
 demo_tx = await dex.get_swap('USDT','wBTC',10)
 print("demo_tx ", demo_tx)
```

### Example

[example](https://github.com/mraniki/dxsp/blob/main/examples/example.py)


### Real use case

[TalkyTrader, submit trading order to CEX & DEX with messaging platform (Telegram, Matrix and Discord)](https://github.com/mraniki/tt)

## Documentation

[![wiki](https://img.shields.io/badge/🪙🗿-wiki-0080ff)](https://talkytrader.gitbook.io/talky/)

