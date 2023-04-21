from dxsp import __version__
from dxsp.assets.blockchains import blockchains

import os, json, requests, asyncio, logging

from config import settings

from web3 import Web3
from pycoingecko import CoinGeckoAPI

from ping3 import ping

class DexSwap:


    def __init__(self,
                 chain_id: int = 1, 
                 wallet_address: str = None,
                 private_key: str = None,
                 block_explorer_api: str = None,
                 block_explorer_url: str = None,
                 rpc: str = None,
                 w3: Web3 = None,
                 protocol_type: str = None,
                 dex_exchange: str = None,
                 dex_router: str = None,
                 base_trading_symbol: str = None,
                 amount_trading_option: int = 1,
                 ):

        self.logger =  logging.getLogger(__name__)
        self.logger.debug(f"DXSP Logger:  {self.logger} on {__name__} version: {__version__}")
        self.logger.info(f"Initializing DexSwap object for {wallet_address} on {chain_id}")

        self.chain_id = int(chain_id)
        self.logger.debug(f"self.chain_id {self.chain_id}")
        if self.chain_id  is None:
            self.logger.warning("self.chain_id not setup")
            return
        blockchain = blockchains[self.chain_id ]
        self.logger.debug(f"blockchain {blockchain}")

        self.wallet_address = wallet_address
        self.logger.debug(f"self.wallet_address {self.wallet_address}")
        self.private_key = private_key

        self.block_explorer_api = block_explorer_api
        if self.block_explorer_api is None:
            self.logger.warning("self.block_explorer_api not setup")
        self.block_explorer_url = block_explorer_url
        self.logger.debug(f"self.block_explorer_url {self.block_explorer_url}")
        if self.block_explorer_url is None:
            self.block_explorer_url = blockchain["block_explorer_url"]
        if self.block_explorer_url is None:
            self.logger.warning("self.block_explorer_url not setup")
        self.logger.debug(f"self.block_explorer_url {self.block_explorer_url}")

        self.rpc = rpc
        if self.rpc is None:
            self.rpc = blockchain["rpc"]
        self.logger.debug(f"self.rpc {self.rpc}")

        self.latency = round(ping(self.rpc, unit='ms'), 3)
        self.logger.debug(f"self.latency {self.latency}")    

        self.w3 = w3
        if self.w3 is None:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc))
            try:
                self.w3.net.listening
                self.logger.info(msg=f"connected to {self.rpc} with w3 {self.w3}")
            except Exception as e:
                self.logger.error(msg=f"connectivity failed using {self.rpc}")
                return
        self.logger.debug(f"self.w3 {self.w3}")
        self.logger.info(msg=f"connected")

        self.protocol_type = protocol_type
        if self.protocol_type is None:
            if self.protocol_type == "0x":
                base_url = blockchain["0x"]
            elif self.protocol_type == "1inch_limit":
                base_url = blockchain["1inch_limit"]
            else:
                base_url = blockchain["1inch"]
                self.protocol_type = "1inch"
            self.dex_url = f"{base_url}"

        self.logger.debug(f"self.dex_url {self.dex_url}")
        self.logger.debug(f"self.protocol_type {self.protocol_type}")

        self.dex_exchange = dex_exchange
        self.logger.debug(f"self.dex_exchange {self.dex_exchange}")

        self.dex_router = dex_router
        if self.dex_router is None:
            if (
                self.dex_exchange is None
                or self.dex_exchange != blockchain["uniswap_v3"]
            ):
                self.router = blockchain["uniswap_v2"]
            else:
                self.router = blockchain["uniswap_v3"]
        self.logger.debug(f"self.router {self.router}")

        self.name = "TBD"
        self.logger.debug(f"self.name {self.name}")        

        self.base_trading_symbol = base_trading_symbol
        if self.base_trading_symbol is None:
            self.base_trading_symbol= 'USDC'
        self.logger.debug(f"self.base_trading_symbol {self.base_trading_symbol}")

        self.amount_trading_option = amount_trading_option
        self.logger.debug(f"self.amount_trading_option {self.amount_trading_option}")

        self.gecko_api = CoinGeckoAPI() # llama_api = f"https://api.llama.fi/" maybe as backup to be reviewed
        assetplatform = self.gecko_api.get_asset_platforms()
        output_dict = [x for x in assetplatform if x['chain_identifier'] == int(self.chain_id)]
        self.gecko_platform = output_dict[0]['id']
        self.logger.debug(f"self.gecko_platform {self.gecko_platform}")

        # self.gasPrice = gasPrice
        
        # self.gasLimit = gasLimit

    async def _get(self, url, params=None, headers=None):
        headers = { "User-Agent": "Mozilla/5.0" }
        self.logger.debug(f"_get url {url}")
        response = requests.get(url,params =params,headers=headers)
        #self.logger.debug(f"response _get {response}")
        return response.json()

    async def get_quote(self, symbol):
        self.logger.debug(f"get_quote {symbol}")
        asset_in_address = await self.search_contract(symbol)
        self.logger.debug(f"asset_in_address {asset_in_address}")
        asset_out_symbol = self.base_trading_symbol
        asset_out_address = await self.search_contract(asset_out_symbol)
        self.logger.debug(f"asset_out_address {asset_out_address}")
        if asset_out_address is None:
            self.logger.debug(f"No Valid Contract {symbol}")
            return
        # asset_out_contract = await self.get_token_contract(asset_out_symbol)
        # asset_out_decimals = asset_out_contract.functions.decimals().call()
        # self.logger.debug(f"asset_out_decimals {asset_out_decimals}")
        try:
            if self.protocol_type == "1inch":
                asset_out_amount = self.w3.to_wei(1,'ether') #1USDC()
                self.logger.debug(f"asset_out_amount {asset_out_amount}")
                quote_url = f"{self.dex_url}/quote?fromTokenAddress={asset_in_address}&toTokenAddress={asset_out_address}&amount={asset_out_amount}"
                quote = await self._get(quote_url)
                self.logger.debug(f"quote {quote}")
                raw_quote = quote['toTokenAmount']
                self.logger.debug(f"raw_quote {raw_quote}")
                asset_quote_decimals = quote['fromToken']['decimals']
                self.logger.debug(f"asset_quote_decimals {asset_quote_decimals}")
                quote_readable = self.w3.from_wei(int(raw_quote),'wei') /(10 ** asset_quote_decimals)
                self.logger.debug(f"quote_readable {quote_readable}")
                return round(quote_readable,2)
            if self.protocol_type in ["uniswap_v2","uniswap_v3"]:
                return
        except Exception as e:
            self.logger.debug(f"error get_quote {e}")
            return

    async def execute_order(self,direction,symbol,stoploss=10000,takeprofit=10000,quantity=1,amount_trading_option=1,order_type='swap'):
        self.logger.debug(f"execute_order {direction} {symbol} {order_type}")
        if order_type == 'swap':
            self.logger.debug(f"execute_order {order_type}")
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
                self.logger.debug(f"error execute_order {e}")
                return

        if order_type == 'market':
            self.logger.debug(f"execute_order {order_type}")
            return
        if order_type == 'limit':
            self.logger.debug(f"execute_order {order_type}")
            return

    async def get_swap(self, 
            asset_out_symbol: str, 
            asset_in_symbol: str,
            amount: int, 
            slippage_tolerance_percentage = 2 
        ):

        self.logger.debug(f"get_swap {asset_out_symbol} {asset_in_symbol} {amount}")
        try:
            
            #ASSET OUT 
            asset_out_address = await self.search_contract(asset_out_symbol)
            asset_out_contract = await self.get_token_contract(asset_out_symbol)
            self.logger.debug(f"asset_out_address {asset_out_address} {asset_out_symbol}")
            if asset_out_contract is None:
                return
            asset_out_decimals=asset_out_contract.functions.decimals().call()
            asset_out_balance = await self.get_token_balance(asset_out_symbol)
            self.logger.debug(f"asset_out_balance {asset_out_balance} {asset_out_symbol}")
            if asset_out_balance == 0:
                self.logger.debug(f"No Money on {asset_out_balance} balance: {asset_out_balance}")
                return 
            #ASSETS IN 
            asset_in_address = await self.search_contract(asset_in_symbol)
            self.logger.debug(f"asset_out_address {asset_out_address} {asset_in_symbol}")
            if asset_in_address is None:
                return

            #AMOUNT
            asset_out_decimals = asset_out_contract.functions.decimals().call()
            self.logger.debug(f"asset_out_decimals {asset_out_decimals}")
            asset_out_amount = amount * 10 ** asset_out_decimals
            slippage = slippage_tolerance_percentage # defaulted to 2% slippage if not given
            self.logger.debug(f"slippage {slippage}")
            asset_out_amount_converted = self.w3.to_wei(amount,'ether')

            transaction_amount = int((asset_out_amount_converted *(slippage/100)))
            self.logger.debug(f"transaction_amount {transaction_amount}")

            #VERIFY IF ASSET OUT IS APPROVED otherwise get it approved
            await self.get_approve(asset_out_address)

            #1INCH
            if self.protocol_type in ["1inch"]:
                swap_url = f"{self.dex_url}/swap?fromTokenAddress={asset_out_address}&toTokenAddress={asset_in_address}&amount={transaction_amount}&fromAddress={self.wallet_address}&slippage={slippage}"
                swap_TX = await self._get(swap_url)
                TX_status_code = swap_TX['statusCode']
                if TX_status_code != 200:
                    return
            #UNISWAP V2
            if self.protocol_type ['uniswap_v2']:
                order_path_dex=[asset_out_address, asset_in_address]
                router_abi = await self.get_abi(self.router)
                router_instance = self.w3.eth.contract(address=self.w3.to_checksum_address(self.router), abi=self.router_abi)
                deadline = self.w3.eth.get_block("latest")["timestamp"] + 3600
                transaction_min_amount  = int(router_instance.functions.getAmountsOut(transaction_amount, order_path_dex).call()[1])
                swap_TX = router_instance.functions.swapExactTokensForTokens(transaction_amount,transaction_min_amount,order_path_dex,self.wallet_address,deadline)
            #1INCH LIMIT
            if self.protocol_type ["1inch_limit"]:
                 return
                # encoded_message = encode_structured_data(eip712_data)
                # signed_message = await sign_transaction_dex(encoded_message)
                # # this is the limit order that will be broadcast to the limit order API
                # limit_order = {
                #     "orderHash": signed_message.messageHash.hex(),
                #     "signature": signed_message.signature.hex(),
                #     "data": order_data,
                # }
                # limit_order_url = dex_1inch_limit_api + str(chain_id) +"/limit-order" # make sure to change the chain_id if you are not using ETH mainnet
                # response = requests.post(url=limit_order_url,headers={"accept": "application/json, text/plain, */*", "content-type": "application/json"}, json=limit_order)

            #UNISWAP V3
            if self.protocol_type ['uniswap_v3']:
                return
            if swap_TX:
                self.logger.debug(f"swap_TX {swap_TX}")
                signed_TX = await self.get_sign(swap_TX)
                transaction_hash = str(self.w3.to_hex(signed_TX))
                #transaction_results = await self.get_block_explorer_status(transaction_hash)
                transaction_hash_details = self.w3.wait_for_transaction_receipt(transaction_hash, timeout=120, poll_latency=0.1)
                if(transaction_hash_details['status'] == "1"):
                    transaction_blockNumber = transaction_hash_details['blockNumber']
                    transaction_receipt = self.w3.eth.get_transaction_receipt(transaction_hash)
                    transaction_block = self.w3.eth.get_block(blockNumber)
                    order={}
                    order['id'] = transaction_receipt['transactionHash']
                    order['timestamp'] = transaction_block['timestamp']
                    order['symbol'] = asset_out_symbol
                    order['contract'] = asset_out_address
                    order['amount'] = transaction_amount
                    order['fee'] = transaction_receipt['gasUsed']
                    order['price'] = 'na'
                    order['confirmation'] = 'na'
                                #response+= f"\n➕ Size: {round(ex.from_wei(transaction_amount, 'ether'),5)}\n⚫️ Entry: {await fetch_gecko_asset_price(asset_in_symbol)}USD \nℹ️ {txHash}\n⛽️ {txHashDetail['gasUsed']}\n🗓️ {datetime.now()}"
            #logger.info(msg=f"{response}")
                    return order
        except Exception as e:
            self.logger.debug(f"error get_swap {e}")
            return

    async def get_block_explorer_status(self,txHash):
        self.logger.debug(f"get_block_explorer_status {txHash}")
        checkTransactionSuccessURL = f"{self.block_explorer_url}?module=transaction&action=gettxreceiptstatus&txhash={txHash}&apikey={self.block_explorer_api}"
        checkTransactionRequest =  self.get(checkTransactionSuccessURL)
        return checkTransactionRequest['status']

####CONTRACT SEARCH

    # async def search_gecko_platform(self):
    #     self.logger.debug("search_gecko_platform")
    #     try:
    #         assetplatform = self.gecko_api.get_asset_platforms()
    #         output_dict = [x for x in assetplatform if x['chain_identifier'] == int(self.chain_id)]
    #         self.logger.debug(f"search_gecko_platform search {output_dict}")
    #         return output_dict[0]['id']
    #     except Exception as e:
    #         self.logger.debug(f"error search_gecko_platform {e}")
    #         return

    async def search_contract(self, token):
        self.logger.debug(f"search_contract {token}")

        try:
            token_contract = await self.get_contract_address(settings.TOKEN_PERSONAL_LIST,token)
            self.logger.debug(f"personal_list {token} {token_contract}")
            if token_contract is None:
                token_contract = await self.get_contract_address(settings.TOKEN_TESTNET_LIST,token)
                self.logger.debug(f"test_token_list {token} {token_contract}")
            if token_contract is None:
                token_contract = await self.get_contract_address(settings.TOKEN_MAINNET_LIST,token)
                self.logger.debug(f"main_list {token} {token_contract}")
            if token_contract is None:
                self.logger.debug(f"gecko search {token}")
                token_contract = await self.search_gecko_contract(token)
            if token_contract is not None:
                self.logger.debug(f"token_contract {token_contract}")
                return self.w3.to_checksum_address(token_contract)
            else:
                self.logger.debug(f"no contract found for {token} on chain {self.chain_id}")
        except Exception as e:
            self.logger.debug(f"error search_contract {e} token {token} token_contract {token_contract}")
            return

    async def search_gecko(self,token):
        self.logger.debug(f"search_gecko {token}")
        try:
            search_results = self.gecko_api.search(query=token)
            search_dict = search_results['coins']
            #self.logger.debug(f"search_dict {search_dict}")
            filtered_dict = [x for x in search_dict if x['symbol'] == token.upper()]
            api_dict = [ sub['api_symbol'] for sub in filtered_dict ]
            self.logger.debug(f"api_dict {api_dict}")
            for i in api_dict:
                coin_dict = self.gecko_api.get_coin_by_id(i)
                try:
                    if coin_dict['platforms'][f'{self.gecko_platform}'] is not None:
                        return coin_dict
                except KeyError:
                    pass
        except Exception as e:
            self.logger.debug(f"error search_gecko {e}")
            return

    async def search_gecko_contract(self,token):
        self.logger.debug(f"🦎search_gecko_contract {token}")
        self.logger.debug(f"🦎self.gecko_platform {self.gecko_platform}")
        try:
            coin_info = await self.search_gecko(token)
            if coin_info is not None:
                coin_info['platforms'][f'{self.gecko_platform}']
                self.logger.debug(f"🦎search_gecko_coin_info {coin_info} {token}")
                return coin_info['platforms'][f'{self.gecko_platform}']
        except Exception as e:
            self.logger.debug(f"error search_gecko_contract {e}")
            return

    async def get_contract_address(self,token_list_url, symbol):
        self.logger.debug(f"get_contract_address {token_list_url} {symbol}")
        try: 
            token_list = await self._get(token_list_url)
            token_search = token_list['tokens']
            for keyval in token_search:
                if (keyval['symbol'] == symbol and keyval['chainId'] == self.chain_id):
                    return keyval['address']
        except Exception as e:
            self.logger.debug(f"error get_contract_address {e}")
            return

    async def get_token_contract(self, token):
        self.logger.debug(f"get_token_contract {token}")
        try:
            token_address = await self.search_contract(token)
            token_abi = await self.get_abi(token_address)
            return self.w3.eth.contract(address=token_address, abi=token_abi)
        except Exception as e:
            self.logger.error(f"error  get_token_contract {e}")
            return


####UTILS
    async def get_approve(self, asset_out_address: str, amount=None):
        self.logger.debug(f"get_approve {asset_out_address}")
        if self.protocol_type in ["1inch","1inch_limit"]:
            approval_check_URL = f"{self.dex_url}/approve/allowance?tokenAddress={asset_out_address}&walletAddress={self.wallet_address}"
            approval_response = await self._get(approval_check_URL)
            approval_check = approval_response['allowance']
            if (approval_check==0):
                approval_URL = f"{self.dex_url}/approve/transaction?tokenAddress={asset_out_address}"
                approval_response = await self._get(approval_URL)
        elif self.protocol_type in ["uniswap_v2","uniswap_v3"]:
            asset_out_abi= await self.get_abi(asset_out_address)
            asset_out_contract = self.w3.eth.contract(address=asset_out_address, abi=asset_out_abi)           
            approval_check = asset_out_contract.functions.allowance(self.w3.to_checksum_address(self.wallet_address), self.w3.to_checksum_address(self.router)).call()
            if (approval_check==0):
                approved_amount = (self.w3.to_wei(2**64-1,'ether'))
                asset_out_abi = await fetch_abi_dex(asset_out_address)
                asset_out_contract = self.w3.eth.contract(address=asset_out_address, abi=asset_out_abi)
                approval_TX = asset_out_contract.functions.approve(self.w3.to_checksum_address(self.router), approved_amount)
                approval_txHash = await sign_transaction_dex(approval_TX)
                approval_txHash_complete = self.w3.eth.wait_for_transaction_receipt(approval_txHash, timeout=120, poll_latency=0.1)

    async def get_sign(self, tx):
        self.logger.debug(f"get_sign {tx}")
        try:
            if self.protocol_type in ['uniswap_v2']:
                tx_params = {
                'from': self.wallet_address,
                'gas': await self.get_gas(tx),
                'gasPrice': await self.get_gasPrice(tx),
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
                }
                tx = tx.build_transaction(tx_params)
            elif self.protocol_type in ['uniswap_v3']:
                tx_params = {
                'from': self.wallet_address,
                'gas': await estimate_gas(tx),
                'gasPrice': await self.get_gasPrice(tx),
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
                }
                tx = tx.build_transaction(tx_params)
            elif self.protocol_type in ["1inch","1inch_limit"]:
                tx = tx['tx']
                tx['gas'] = await estimate_gas(tx)
                tx['nonce'] = self.w3.eth.get_transaction_count(self.wallet_address)
                tx['value'] = int(tx['value'])
                tx['gasPrice'] = await self.get_gasPrice(tx)
            signed = self.w3.eth.account.sign_transaction(tx, self.private_key)
            raw_tx = signed.rawTransaction
            return self.w3.eth.send_raw_transaction(raw_tx)
        except Exception as e:
            self.logger.debug(f"error get_sign {e}")
            return

    async def get_gas(self, tx):
        self.logger.debug(f"get_gas {tx}")
        gasestimate= self.web3.eth.estimate_gas(tx) * 1.25
        return int(self.w3.to_wei(gasestimate,'wei'))

    async def get_gasPrice(self, tx):
        self.logger.debug(f"get_gasPrice {tx}")
        gasprice= self.w3.eth.generate_gas_price()
        return self.w3.to_wei(gasPrice,'gwei')

    async def get_abi(self,addr):
        self.logger.debug(f"get_abi {addr}")
        if self.block_explorer_api is None:
            self.logger.debug("No block_explorer_api")
        try:
            params = {
                "module": "contract",
                "action": "getabi",
                "address": addr,
                "apikey": self.block_explorer_api }
            headers = { "User-Agent": "Mozilla/5.0" }
            resp = await self._get(url=self.block_explorer_url,params=params,headers=headers)
            #self.logger.debug(f"resp {resp} status {resp['status']}")
            if resp['status']=="1":
                self.logger.debug(f"ABI found {resp}")
                abi = resp["result"]
                return abi
            else:
                self.logger.debug(f"No ABI identified Option B needed for contract {addr} on chain {self.chain_id}")
                # https://github.com/tintinweb/smart-contract-sanctuary
                #https://raw.githubusercontent.com/tintinweb/smart-contract-sanctuary-optimism/master/contracts/mainnet/1f/1F98431c8aD98523631AE4a59f267346ea31F984_UniswapV3Factory.sol

        except Exception as e:
            self.logger.debug(f"error get_abi {e}")
            return

#####USERS

    async def get_wallet_auth():
        try:
            return
        except Exception as e:
            self.logger.error(msg=f"get_wallet_auth error: {e}")
            return

    async def get_token_balance(self, token):
        self.logger.debug(f"get_token_balance {token}")
        try:
            token_address = await self.search_contract(token)
            token_abi =  await self.get_abi(token_address)
            token_contract = self.w3.eth.contract(address=token_address, abi=token_abi)
            token_balance = token_contract.functions.balanceOf(self.wallet_address).call()
            logger.debug(msg=f"token_address {token_address} token_balance {token_balance}")
            # (ex.from_wei(await fetch_token_balance(basesymbol), 'ether'), 5)
            return 0 if token_balance <=0 or token_balance is None else token_balance
        except Exception as e:
            logger.error(msg=f"{token} get_token_balance error: {e}")
            return 0

    async def get_basecoin_balance(self):
        bal_base_trading_symbol = await self.get_token_balance(self.base_trading_symbol)
            # return round(ex.from_wei(await fetch_token_balance(basesymbol), 'ether'), 5)
        return bal_base_trading_symbol
        # bal = round(ex.from_wei(bal,'ether'),5)

    async def get_stablecoin_balance(self):
        toptokens = ["USDT","USDC","BUSD","DAI"]
        for i in toptokens:
            bal_toptoken = await self.get_token_balance(i)
            if bal_toptoken:
                msg += f"\n💵{bal_toptoken} {i}"
            # bal = round(ex.from_wei(bal,'ether'),5)

    async def get_account_balance(self):
        toptokens = ["WBTC","ETH","BNB","UNI"]
        for i in toptokens:
            bal_toptoken = await self.get_token_balance(i)
            if bal_toptoken:
                msg += f"\n💵{bal_toptoken} {i}"
            # bal = round(ex.from_wei(bal,'ether'),5)

    async def get_account_position(self):
        self.logger.debug(f"get_account_position")
        try:
            # asset_position_address= await search_contract(asset_out_symbol)
            # asset_position_abi= await fetch_abi_dex(asset_out_address)
            # asset_position_contract = ex.eth.contract(address=asset_out_address, abi=asset_out_abi)
            # open_positions = asset_position_contract.functions.getOpenPositions(walletaddress).call()
            return
        except Exception as e:
            logger.error(msg=f"get_account_position error: {e}")
            return 0

    # async def fetch_account_dex(addr):
    #     url = block_explorer_url
    #     query = {'module':'account',
    #             'action':'tokenbalance',
    #             'contractaddress':addr,
    #             'address':walletaddress,
    #             'tag':'latest',
    #             'apikey':block_explorer_api}
    #     r = requests.get(url, params=query)
    #     try:
    #         d = json.loads(r.text)
    #     except:
    #         return None
    #     return int(d['result']) / self.zeroes

#     async def fetch_gecko_asset_price(token):
#     try:
#         asset_in_address = ex.to_checksum_address(await search_contract(token))
#         fetch_tokeninfo = gecko_api.get_coin_info_from_contract_address_by_id(id=f'{coin_platform}',contract_address=asset_in_address)
#         return fetch_tokeninfo['market_data']['current_price']['usd']
#     except Exception:
#         return

# async def fetch_gecko_quote(token):
#     try:
#         asset_in_address = ex.to_checksum_address(await search_contract(token))
#         fetch_tokeninfo = gecko_api.get_coin_info_from_contract_address_by_id(id=f'{coin_platform}',contract_address=asset_in_address)
#         logger.debug(msg=f"fetch_tokeninfo {fetch_tokeninfo}")
#         asset_out_cg_quote = fetch_tokeninfo['market_data']['current_price']['usd']
#         asset_out_cg_name = fetch_tokeninfo['name']
#         return f"{asset_out_cg_name}\n🦎{asset_out_cg_quote} USD"
#     except Exception:
#         return

