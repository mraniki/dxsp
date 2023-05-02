"""
DXSP Example
"""
from dxsp import DexSwap, settings

import sys
import os
import asyncio
import requests
import logging
#from dotenv import load_dotenv
import random

from fastapi import FastAPI
import uvicorn

#YOUR VARIABLES
#load_dotenv()
sys.path.append('../')

#chain ID being used refer to https://chainlist.org/
#chain = os.getenv("CHAIN_ID", 10)

#your wallet details
#wallet_address = os.getenv("WALLET_ADDRESS", "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
#private_key = os.getenv("PRIVATE_KEY", "0x111111111117dc0aa78b770fa6a738034120c302")

#Block explorer API from ETHERSCAN TYPE EXPLORER
#block_explorer_api = os.getenv("BLOCK_EXPLORER_API", "1X23Q4ACZ5T3KXG67WIAH7X8C510F1972TM")


#DEBUG LEVEL
logging.basicConfig(level=logging.DEBUG)


async def main():
	while True:
		chain_lst = ['1','56','42161','137','10','43114','250']
		chain = random.sample(chain_lst,1)[0]
		print("chain ", chain)

		#SWAP HELPER
		dex = DexSwap(
					chain_id=chain,
					wallet_address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
					private_key="0x111111111117dc0aaaaaa0fa6a738034aaaa302",
					block_explorer_api=block_explorer_api
				)
		print(type(dex))
		print(type(dex.chain_id))
        print(isinstance(dex,dxsp.main.DexSwap)
        print(isinstance(dex,DexSwap)
		#BUY 10 USDC to SWAP with BITCOIN
		#demo_tx = await dex.get_swap('USDT','wBTC',10)
		#print("demo_tx ", demo_tx)

		#SWAP with your OWN defined exchange like Sushiswap on ARBITRUM 
		# sushi_router = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'
		# dex_sushi = DexSwap(chain_id=42161,wallet_address=wallet_address,private_key=private_key,block_explorer_api=block_explorer_api,dex_exchange=sushi_router,base_trading_symbol='USDT')
		# print("dex_sushi ", dex_sushi)
		# #Execute ORDER to buy 1% of your USDT balance on SUSHISWAP ARBITRUM and get BTC token
		# demo_order = await dex_sushi.execute_order(direction = 'BUY',symbol = 'wBTC')
		# print("demo_order ", demo_order)
		
		#QUOTE
		#symbol = 'BNB'
		symbol_lst = ['WBTC','APE','KAVA','WETH','MATIC','UNI','CAKE','USDT','DAI','AAVE','SUSHI','CRV','ALPACA','ANY','MIM']
		symbol = random.sample(symbol_lst,1)[0]
		print("symbol ", symbol)
		# quote = await dex.get_quote(symbol)
		# print("quote ", quote)
		
		# #get Contract Address
		address = await dex.search_contract(symbol)
		print("chain ",chain,"symbol ",symbol," address ", address)
		#bitcoinaddress  0x68f180fcCe6836688e9084f035309E29Bf0A2095

		#getABI
		addressABI = await dex.get_abi(address)
		# print("ABI ", addressABI)

		try:
		    requests.get("https://hc-ping.com/e4d29002-cc1a-487c-8510-9e791cd356fb", timeout=10)
		except requests.RequestException as e:
		    # Log ping failure here...
		    print(f"Ping failed: {e}")

		await asyncio.sleep(3600)


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
    HOST=os.getenv("HOST", "0.0.0.0")
    PORT=os.getenv("PORT", "8080")
    uvicorn.run(app, host='0.0.0.0', port=8080)

