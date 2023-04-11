import os
import logging
from dotenv import load_dotenv
import json
import requests
import asyncio
from web3 import Web3
from pycoingecko import CoinGeckoAPI

from dxsp.assets.blockchains import blockchains

#🧐LOGGING
LOGLEVEL=os.getenv("LOGLEVEL", "DEBUG")
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=LOGLEVEL)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.info(msg=f"LOGLEVEL {LOGLEVEL}")

class DexSwap:


    #🦎GECKO
    gecko_api = CoinGeckoAPI() # llama_api = f"https://api.llama.fi/" maybe as backup to be reviewed

    def __init__(self,
                 chain_id = 1, 
                 wallet_address = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE,
                 private_key = 0x111111111117dc0aa78b770fa6a738034120c302,
                 block_explorer_api: str = None,
                 w3: Web3 = None,
                 protocol_type= "1inch",
                 dex_exchange = 'uniswap_v2',
                 base_trading_symbol = 'USDC',
                 amount_trading_option = 1,
                 ):
        self.chain_id = int(chain_id)
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.block_explorer_api = block_explorer_api

        self.w3 = w3
        self.protocol_type = protocol_type
        self.dex_exchange = dex_exchange
        self.base_trading_symbol = base_trading_symbol
        self.amount_trading_option = amount_trading_option

        blockchain = blockchains[self.chain_id]
        logger.debug(msg=f"blockchain {blockchain}")

        self.block_explorer_url = blockchain["block_explorer_url"]
        self.rpc = blockchain["rpc"]

        if self.protocol_type == "1inch":
            base_url = self.block_explorer_url = blockchain["1inch"]
            self.dex_url = f"{base_url}"
            logger.debug(msg=f"dex_url {self.dex_url}")
        if self.protocol_type == "1inch_limit":
            base_url = self.block_explorer_url = blockchain["1inch_limit"]
            self.dex_url = f"{base_url}"
            logger.debug(msg=f"dex_url {self.dex_url}")
        if self.protocol_type == "0x":
            base_url = self.block_explorer_url = blockchain["0x"]
            self.dex_url = f"{base_url}"
            logger.debug(msg=f"dex_url {self.dex_url}")

        if self.w3 == "":
            self.w3 = Web3(Web3.HTTPProvider(self.rpc))

        if self.dex_exchange == "":
            if self.protocol_type == "uniswap_v3":
                self.dex_exchange = blockchain["uniswap_v3"]
                self.router = blockchain["uniswap_v3"]
            else:
                self.dex_exchange = blockchain["uniswap_v2"]
                self.router = blockchain["uniswap_v2"]

    @staticmethod
    def _get(url, params=None, headers=None):
        logger.debug(msg=f"url {url}")
        headers = { "User-Agent": "Mozilla/5.0" }
        response = requests.get(url,params =params,headers=headers)
        #logger.debug(msg=f"response {response}")
        #logger.debug(msg=f"response json {response.json()}")
        return response.json()

    async def get_quote(self, symbol):
            asset_in_address = await self.search_contract(symbol)
            logger.debug(msg=f"asset_in_address {asset_in_address}")
            asset_out_address = await self.search_contract('USDC')
            logger.debug(msg=f"asset_out_address {asset_out_address}")
            try:
                if self.protocol_type == 1:
                    asset_out_amount=1000000000000
                    quote_url = f"{self.dex_url}/quote?fromTokenAddress={asset_in_address}&toTokenAddress={asset_out_address}&amount={asset_out_amount}"
                    logger.debug(msg=f"quote_url {quote_url}")
                    quote = self._get(quote_url)
                    logger.debug(msg=f"quote {quote}")
                    return quote['toTokenAmount']
                if self.protocol_type in [2,4]:
                    return
            except Exception as e:
                logger.debug(msg=f"error {e}")
                return

    async def get_abi(self,addr):
        try:
            url = self.block_explorer_url
            logger.debug(msg=f"url {url}")
            logger.debug(msg=f"addr {addr}")
            params = {
                "module": "contract",
                "action": "getabi",
                "address": addr,
                "apikey": self.block_explorer_api }
            headers = { "User-Agent": "Mozilla/5.0" }
            print(url,params,headers)
            resp = requests.get(url=url,params =params,headers=headers)
            print(resp)
            response = resp.json() 
            logger.debug(msg=f"response {response}")
            abi = response["result"]
            logger.debug(msg=f"abi {abi}")
            return abi if (abi!="") else None
        except Exception as e:
            logger.debug(msg=f"error {e}")
            return

    async def get_approve(self, asset_out_address: str, amount=None):
        if self.protocol_type in ["1"]:
            approval_check_URL = f"{self.dex_url}/approve/allowance?tokenAddress={asset_out_address}&walletAddress={self.wallet_address}"
            approval_response =  self._get(approval_check_URL)
            approval_check = approval_response['allowance']
            if (approval_check==0):
                approval_URL = f"{self.dex_url}/approve/transaction?tokenAddress={asset_out_address}"
                approval_response =  self._get(approval_URL)
        elif self.protocol_type in ["2", "4"]:
            asset_out_abi= await self.get_abi(asset_out_address)
            asset_out_contract = self.w3.eth.contract(address=asset_out_address, abi=asset_out_abi)           
            approval_check = asset_out_contract.functions.allowance(self.w3.to_checksum_address(self.wallet_address), self.w3.to_checksum_address(self.router)).call()
            logger.debug(msg=f"approval_check {approval_check}")
            if (approval_check==0):
                approved_amount = (self.w3.to_wei(2**64-1,'ether'))
                asset_out_abi = await fetch_abi_dex(asset_out_address)
                asset_out_contract = self.w3.eth.contract(address=asset_out_address, abi=asset_out_abi)
                approval_TX = asset_out_contract.functions.approve(self.w3.to_checksum_address(self.router), approved_amount)
                approval_txHash = await sign_transaction_dex(approval_TX)
                approval_txHash_complete = self.w3.eth.wait_for_transaction_receipt(approval_txHash, timeout=120, poll_latency=0.1)

    async def get_sign(self, tx):
        try:
            if self.protocol_type in ['2']:
                tx_params = {
                'from': self.wallet_address,
                'gas': await self.get_gas(tx),
                'gasPrice': await self.get_gasPrice(tx),
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
                }
                tx = tx.build_transaction(tx_params)
            elif self.protocol_type in ['4']:
                tx_params = {
                'from': self.wallet_address,
                'gas': await estimate_gas(tx),
                'gasPrice': self.w3.to_wei(gasPrice,'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
                }
                tx = tx.build_transaction(tx_params)
            elif self.protocol_type == 1:
                tx = tx['tx']
                tx['gas'] = await estimate_gas(tx)
                tx['nonce'] = self.w3.eth.get_transaction_count(self.wallet_address)
                tx['value'] = int(tx['value'])
                tx['gasPrice'] = int(ex.to_wei(gasPrice,'gwei'))
            signed = self.w3.eth.account.sign_transaction(tx, self.private_key)
            raw_tx = signed.rawTransaction
            return self.w3.eth.send_raw_transaction(raw_tx)
        except Exception as e:
            logger.debug(msg=f"sign_transaction error {e}")
            return

    async def get_gas(tx):
        gasestimate= self.web3.eth.estimate_gas(tx) * 1.25
        logger.debug(msg=f"gasestimate {gasestimate}")
        return int(self.w3.to_wei(gasestimate,'wei'))

    async def get_gasPrice(tx):
        gasprice= self.w3.eth.generate_gas_price()
        logger.debug(msg=f"gasprice {gasprice}")
        return self.w3.to_wei(gasPrice,'gwei')

    
    async def execute_order(self,direction,symbol,stoploss,takeprofit,quantity,amount_trading_option=1):

        try:
            asset_out_symbol = self.base_trading_symbol if direction=="BUY" else symbol
            asset_in_symbol = symbol if direction=="BUY" else self.base_trading_symbol
            asset_out_contract = await self.get_token_contract(asset_out_symbol)
            asset_out_decimals = asset_out_contract.functions.decimals().call()
            asset_out_balance = await self.get_token_balance(asset_out_symbol)
            if amount_trading_option == 1:
                asset_out_amount = ((asset_out_balance)/(10 ** asset_out_decimals))*(float(quantity)/100) #buy or sell %p percentage DEFAULT OPTION
            if amount_trading_option == 2:
                asset_out_amount = (asset_out_balance)/(10 ** asset_out_decimals) #SELL all token in case of sell order for example
      
            swap = self.get_swap(asset_out_symbol,asset_in_symbol,asset_out_amount)

        except Exception as e:
            logger.debug(msg=f"execute_order error {e}")
            return  

    async def get_swap(self, 
            asset_out_symbol: str, 
            asset_in_symbol: str,
            amount: int, 
            slippage_tolerance_percentage = 2 
        ):


        try:
            
            #ASSET OUT 
            asset_out_address = await self.search_contract(asset_out_symbol)
            asset_out_contract = await self.get_token_contract(asset_out_symbol)
            logger.debug(msg=f"asset_out_contract {asset_out_contract}")
            if asset_out_contract is None:
                logger.warning(msg=f"{asset_out_symbol} not supported")
                return
            asset_out_decimals=asset_out_contract.functions.decimals().call()
            logger.debug(msg=f"asset_out_decimals {asset_out_decimals}")
            asset_out_balance = await self.get_token_balance(asset_out_symbol)

            #ASSETS IN 
            asset_in_address = await self.search_contract(asset_in_symbol)
            logger.debug(msg=f"asset_in_address {asset_in_address}")
            if asset_in_address is None:
                logger.warning(msg=f"{asset_in_symbol} not supported")
                return

            #AMOUNT
            asset_out_decimals = asset_out_contract.functions.decimals().call()
            asset_out_amount = amount * 10 ** asset_out_decimals
            slippage = slippage_tolerance_percentage # defaulted to 2% slippage if not given
            asset_out_amount_converted = self.w3.to_wei(amount,'ether')

            transaction_amount = int((asset_out_amount_converted *(slippage/100)))

            #VERIFY IF ASSET OUT IS APPROVED
            await self.get_approve(asset_out_address)

            #1INCH
            if self.protocol_type == 1:
                swap_url = f"{self.dex_url}/swap?fromTokenAddress={asset_out_address}&toTokenAddress={asset_in_address}&amount={transaction_amount}&fromAddress={self.wallet_address}&slippage={slippage}"
                swap_TX = self._get(swap_url)
                TX_status_code = swap_TX['statusCode']
                if TX_status_code != 200:
                    logger.debug(msg=f"{TX_status_code}")
                    logger.warning(msg=f"{swap_TX['description']}")
                    return
            #UNISWAP V2
            if self.protocol_type == 2:
                order_path_dex=[asset_out_address, asset_in_address]
                router_abi = await self.get_abi(self.router)
                router_instance = self.w3.eth.contract(address=self.w3.to_checksum_address(self.router), abi=self.router_abi)
                deadline = self.w3.eth.get_block("latest")["timestamp"] + 3600
                transaction_min_amount  = int(router_instance.functions.getAmountsOut(transaction_amount, order_path_dex).call()[1])
                swap_TX = router_instance.functions.swapExactTokensForTokens(transaction_amount,transaction_min_amount,order_path_dex,self.wallet_address,deadline)
            #1INCH LIMIT
            if self.protocol_type == 3:
                 return
            #UNISWAP V3
            if self.protocol_type == 4:
                return
            if swap_TX:
                signed_TX = await self.get_sign(swap_TX)
                txHash = str(self.w3.to_hex(signed_TX))
                logger.debug(msg=f"txHash {txHash}")
                txResult = await self.get_block_explorer_status(txHash)
                logger.debug(msg=f"txResult {txResult}")
                txHashDetail= self.w3.wait_for_transaction_receipt(txHash, timeout=120, poll_latency=0.1)
                logger.debug(msg=f"txHashDetail {txHashDetail}")
                if(txResult == "1"):
                    return txHash
        except Exception as e:
            logger.error(msg=f"swap error {e}")
            return

    async def get_block_explorer_status (txHash):
        checkTransactionSuccessURL = f"{self.block_explorer_url}?module=transaction&action=gettxreceiptstatus&txhash={txHash}&apikey={self.block_explorer_api}"
        logger.debug(msg=f"checkTransactionSuccessURL {checkTransactionSuccessURL}")
        checkTransactionRequest =  self.get(checkTransactionSuccessURL)
        logger.debug(msg=f"checkTransactionRequest {checkTransactionRequest}")
        return checkTransactionRequest['status']

    async def search_gecko_contract(self,token):
        try:
            coin_info = await self.search_gecko(token)
            coin_contract = coin_info['platforms'][f'{coin_platform}']
            logger.debug(msg=f"🦎 contract {token} {coin_contract}")
            return coin_contract
        except Exception:
            return

    async def search_gecko(self,token):
        try:
            search_results = gecko_api.search(query=token)
            search_dict = search_results['coins']
            filtered_dict = [x for x in search_dict if x['symbol'] == token.upper()]
            api_dict = [ sub['api_symbol'] for sub in filtered_dict ]
            for i in api_dict:
                coin_dict = gecko_api.get_coin_by_id(i)
                try:
                    coin_platform = await self.search_gecko_platform()
                    if coin_dict['platforms'][f'{coin_platform}'] is not None:
                        return coin_dict
                except KeyError:
                    pass
        except Exception as e:
            logger.error(msg=f"search_gecko error {e}")
            return

    async def search_gecko_platform(self):
        try:
            assetplatform = gecko_api.get_asset_platforms()
            output_dict = [x for x in assetplatform if x['chain_identifier'] == int(self.chain_id)]
            return output_dict[0]['id']
        except Exception as e:
            logger.debug(msg=f"search_gecko_platform error {e}")

    async def get_contract_address(self,token_list_url, symbol):
        try: 
            token_list = self._get(token_list_url)
            #logger.debug(msg=f"symbol {symbol}")
            token_search = token_list['tokens']
            for keyval in token_search:
                if (keyval['symbol'] == symbol and keyval['chainId'] == self.chain_id):
                    #logger.debug(msg=f"keyval {keyval['address']}")
                    return keyval['address']
        except Exception as e:
            return

    async def search_contract(self, token):
        #📝tokenlist
        main_list = 'https://raw.githubusercontent.com/viaprotocol_type/tokenlists/main/all_tokens/all.json'
        personal_list = os.getenv("TOKENLIST", "https://raw.githubusercontent.com/mraniki/tokenlist/main/TT.json") 
        test_token_list=os.getenv("TESTTOKENLIST", "https://raw.githubusercontent.com/mraniki/tokenlist/main/testnet.json")

        try:
            token_contract = await self.get_contract_address(main_list,token)
            if token_contract is None:
                token_contract = await self.get_contract_address(test_token_list,token)
                if token_contract is None:
                    token_contract = await self.get_contract_address(personal_list,token)
                    if token_contract is None:
                        token_contract = await self.search_gecko_contract(token)
            if token_contract:
                return self.w3.to_checksum_address(token_contract)
        except Exception as e:
            logger.error(msg=f"search_contract error {token} {e}")

    async def get_token_contract(self, token):
        try:
            token_address= await self.search_contract(token)
            token_abi= await self.get_abi(token_address)
            token_contract = self.w3.eth.contract(address=token_address, abi=token_abi)
            return token_contract
        except Exception as e:
            logger.error(msg=f"get_token_contract error {token} {e}")

    async def get_token_balance(self, token):
        try:
            token_contract = await self.get_token_contract(token)
            token_balance = token_contract.functions.balanceOf(self.wallet_address).call()
            logger.debug(msg=f"token {token} token_balance {token_balance}")
            return 0 if token_balance <=0 or token_balance is None else token_balance
        except Exception as e:
            logger.error(msg=f"{token} get_token_balance error: {e}")
            return 0

if __name__ == '__main__':
    pass