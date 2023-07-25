"""
DXSP Example
"""
import asyncio
import sys

import uvicorn
from fastapi import FastAPI
from loguru import logger

from dxsp import DexSwap
from dxsp.config import settings

logger.remove()
logger.add(sys.stderr, level="INFO")
 


async def main():
    while True:
        # SWAP HELPER
        dex = DexSwap()
        # print(type(dex))
        print(settings.VALUE)

        # settings.setenv()
        print(dex.account)
        symbol = 'WBTC'

        # # Contract Address
        address = await dex.contract_utils.search_contract_address(symbol)
        print("address ", address)
        # # token_contract found 0x2260fac5e5542a773aa44fbcfedf7c193bc2c599

        # # get contract and underlying ABI
        token_contract = await dex.contract_utils.get_token_contract(address)
        print("Contract ", token_contract)
        # Contract  <web3._utils.datatypes.Contract object at 0x10acdb050>

        quote = await dex.get_quote(symbol)
        print("quote ", quote)
        # quote  🦄 29761.19589 USDT

        # # BUY 10 USDC to SWAP with BITCOIN
        # demo_tx = await dex.get_swap('USDT','WBTC',10)
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
