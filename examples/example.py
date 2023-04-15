import sys
sys.path.append('../')
import logging
import os
import time
import requests 
import random

from fastapi import FastAPI
import uvicorn


from dotenv import load_dotenv
import asyncio
from web3 import Web3


#YOUR VARIABLES
load_dotenv()
healthchecks_io_api = os.getenv("HEALTHCHECK_API", "1X23Q4ACZ5T3KXG67WIAH7X8C510F191234")
healthchecks_io_uuid = os.getenv("HEALTHCHECK_UUID", "https://hc-ping.com/e4d29002-cc1a-487c-8510-9e791cd356fb")

#chain ID being used refer to https://chainlist.org/
chain = os.getenv("CHAIN_ID", 10)

#your wallet details
wallet_address = os.getenv("WALLET_ADDRESS", "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
private_key = os.getenv("PRIVATE_KEY", "0x111111111117dc0aa78b770fa6a738034120c302")

#Block explorer API from ETHERSCAN TYPE EXPLORER
block_explorer_api = os.getenv("BLOCK_EXPLORER_API", "1X23Q4ACZ5T3KXG67WIAH7X8C510F1972TM")

#OPTIONAL PARAMETERS
#network_provider_url = os.getenv("NETWORK_PROVIDER_URL")

#DEX CONNECTIVITY
#w3 = Web3(Web3.HTTPProvider(network_provider_url))


# protocol_type = os.getenv("protocol_type", "uniswap_v2")
# dex_exchange = os.getenv("DEX_EXCHANGE", '0x1F98431c8aD98523631AE4a59f267346ea31F984')
# base_trading_symbol = os.getenv("BASE_TRADE_SYMBOL", 'USDT')
# amount_trading_option = os.getenv("AMOUNT_TRADING_OPTION", 1)

from dxsp.main import DexSwap
#DEBUG LEVEL for DXSP package
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('dxsp.__main__').setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.WARNING)


async def main():
	while True:

		healthcheck = requests.get(url= healthchecks_io_uuid, timeout=10)
		#SWAP HELPER

		chain_lst = ['1','11155111','56','42161','137','10','43114','250','42220']
		chain = random.sample(chain_lst,1)[0]
		print("chain ", chain)
		dex = DexSwap(chain_id=chain,wallet_address=wallet_address,private_key=private_key,block_explorer_api=block_explorer_api)

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
		symbol_lst = ['WBTC','BTC','ETH','WETH','MATIC','UNI','CAKE','USDT','DAI','AAVE','SUSHI','CRV','UNCX','BIFI']
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
		time.sleep(240)

app = FastAPI()

@app.get("/")
def read_root():
    loop = asyncio.get_event_loop()
    loop.create_task(main())

@app.get("/health")
def health_check():
    return {"DXSP is online"}


if __name__ == "__main__":
    HOST=os.getenv("HOST", "0.0.0.0")
    PORT=os.getenv("PORT", "8080")
    uvicorn.run(app, host='0.0.0.0', port=8080)

