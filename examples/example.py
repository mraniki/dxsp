"""
DXSP Example
"""
import asyncio
import logging
import random

from fastapi import FastAPI
import uvicorn

from dxsp import DexSwap

# DEBUG LEVEL
logging.basicConfig(level=logging.DEBUG)


async def main():
    while True:
        # SWAP HELPER
        dex = DexSwap()
        print(type(dex))

        # RANDOM SYMBOL
        symbol_lst = [
            'WBTC', 'WETH', 'MATIC', 'UNI',
            'USDT', 'DAI']
        symbol = random.sample(symbol_lst, 1)[0]
        print("symbol ", symbol)

        # Contract Address
        address = await dex.search_contract(symbol)
        # token_contract found 0xdac17f958d2ee523a2206206994597c13d831ec7

        # getABI
        addressABI = await dex.get_abi(address)
        print("ABI ", addressABI)

        quote = await dex.get_quote(symbol)
        print("quote ", quote)

        # BUY 10 USDC to SWAP with BITCOIN
        # demo_tx = await dex.get_swap('USDT','wBTC',10)
        # print("demo_tx ", demo_tx)

        await asyncio.sleep(7200)


app = FastAPI()


@app.on_event('startup')
async def start():
    asyncio.create_task(main())


@app.get("/")
def read_root():
    return {"DXSP is online"}


@app.get("/health")
def health_check():
    return {"DXSP is online"}


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8080)
