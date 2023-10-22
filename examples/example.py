"""
DXSP Example
"""
import asyncio
import logging

from dxsp import DexSwap

logging.basicConfig()


async def main():
    logging.getLogger().setLevel(logging.DEBUG)
    dex = DexSwap()
    symbol = "BTC"

    quote = await dex.get_quotes(symbol)
    print("quote ", quote)
    # quote  🦄 29761.19589 USDT

    # # BUY 10 USDC to SWAP with BITCOIN
    # tx = await dex.execute_order('USDT','BTC',10)
    # print("tx ", tx)


if __name__ == "__main__":
    asyncio.run(main())
