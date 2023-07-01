# DXSP (DeX SwaP)

|<img width="200" alt="Logo" src="https://user-images.githubusercontent.com/8766259/231213427-63ea2752-13d5-4993-aee2-90671b57fc6e.png">  | A python defi swap helper package. Swap made easy |
| ------------- | ------------- |
|[![wiki](https://img.shields.io/badge/🪙🗿-wiki-0080ff)](https://talkytrader.gitbook.io/talky/) [![Pypi](https://badgen.net/badge/icon/dxsp?icon=pypi&label)](https://pypi.org/project/dxsp/) ![Version](https://img.shields.io/pypi/v/dxsp)<br>  ![Pypi](https://img.shields.io/pypi/dm/dxsp) <br>[![👷Flow](https://github.com/mraniki/dxsp/actions/workflows/%F0%9F%91%B7Flow.yml/badge.svg)](https://github.com/mraniki/dxsp/actions/workflows/%E2%9C%A8Flow.yml)<br>[![codebeat badge](https://codebeat.co/badges/b1376839-73bc-4b41-bfc1-2fb099f1fc2a)](https://codebeat.co/projects/github-com-mraniki-dxsp-main)<br>[![codecov](https://codecov.io/gh/mraniki/dxsp/branch/main/graph/badge.svg?token=39ED0ZA6IH)](https://codecov.io/gh/mraniki/dxsp) <br>[![Web3](https://badgen.net/badge/icon/web3/black?icon=libraries&label)](https://github.com/ethereum/web3.py) [![coingecko](https://badgen.net/badge/icon/coingecko/black?icon=libraries&label)](https://github.com/coingecko)|Key blockchains (ETH, BSC, ARB, MATIC, OPT...)<br>Key swap protocol (UniV2 0x)

Key features:

- Any blockchains mainnet or testnet supported by web3py, uniswap type router (uniswap, pancakeswap) or 0x.


Other features:

- Translate token symbol to contract address via user defined tokenlist format or coingecko API
- Connect to web3 automatically or use your own w3
- Approve contract and sign transaction
- Quote a given token
- Use Base trading symbol like stablecoin for risk management approach
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

[TalkyTrader](https://github.com/mraniki/tt)

## Documentation

[![wiki](https://img.shields.io/badge/🪙🗿-wiki-0080ff)](https://talkytrader.gitbook.io/talky/)

