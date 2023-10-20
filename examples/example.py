"""
DXSP Example
"""
import asyncio
import sys

import uvicorn
from fastapi import FastAPI
from loguru import logger

from dxsp import DexSwap

logger.remove()
logger.add(sys.stderr, level="DEBUG")


async def main():
    while True:
        dex = DexSwap()
        symbol = "BTC"

        quote = await dex.get_quotes(symbol)
        print("quote ", quote)
        # quote  🦄 29761.19589 USDT

        # # BUY 10 USDC to SWAP with BITCOIN
        # tx = await dex.execute_order('USDT','BTC',10)
        # print("tx ", tx)

        await asyncio.sleep(7200)


app = FastAPI()


@app.on_event("startup")
async def start():
    asyncio.create_task(main())


@app.get("/")
def read_root():
    return {"DXSP is online"}


@app.get("/health")
def health_check():
    return {"DXSP is online"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
