"""
 DEX SWAP Main
"""

import logging

import requests
from dxsp import __version__
from dxsp.assets.blockchains import blockchains
from dxsp.config import settings
from ping3 import ping
from pycoingecko import CoinGeckoAPI
from web3 import Web3


class DexSwap:
    """Do a swap."""

    def __init__(self,
                 chain_id: int = 1,
                 wallet_address: str | None = None,
                 private_key: str | None = None,
                 block_explorer_api: str | None = None,
                 block_explorer_url: str | None = None,
                 rpc: str | None = None,
                 w3: Web3 | None = None,
                 protocol_type: str | None = None,
                 router_contract_addr: str | None = None,
                 ):
        """build a web3 object for swap"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("DexSwap version: %s", __version__)
        self.logger.info("Initializing DexSwap for %s on %s",
                         wallet_address, chain_id)

        self.chain_id = int(chain_id)
        self.logger.debug("self.chain_id %s", self.chain_id)
        if self.chain_id is None:
            self.logger.warning("self.chain_id not setup")
            return
        blockchain = blockchains[self.chain_id]
        self.logger.debug("blockchain %s", blockchain)

        self.wallet_address = wallet_address
        self.logger.debug("self.wallet_address %s", self.wallet_address)
        self.private_key = private_key

        self.block_explorer_api = block_explorer_api
        if self.block_explorer_api is None:
            self.logger.warning("self.block_explorer_api not setup")
        self.block_explorer_url = block_explorer_url
        self.block_explorer_url = (
            block_explorer_url
            or blockchain.get("block_explorer_url")
            or self.logger.warning("self.block_explorer_url not set up")
        )
        self.logger.debug("explorer_url %s", self.block_explorer_url)

        self.rpc = rpc or blockchain.get("rpc")
        self.logger.debug("self.rpc %s", self.rpc)
        try:
            self.latency = round(ping(self.rpc, unit='ms'), 3)
            self.logger.debug("self.latency %s", self.latency)
        except Exception as e:
            self.logger.error("Failed to ping %s:%s", self.rpc, e)

        self.w3 = w3 or Web3(Web3.HTTPProvider(self.rpc))
        try:
            self.w3.net.listening
            self.logger.info("connected to %s with w3 %s", self.rpc, self.w3)
        except Exception as e:
            self.logger.error("connectivity failed %s", e)
            return
        self.logger.debug("self.w3 %s", self.w3)
        self.logger.info("connected")

        self.protocol_type = protocol_type or "1inch"
        if self.protocol_type == "0x":
            base_url = blockchain["0x"]
        elif self.protocol_type == "1inch_limit":
            base_url = blockchain["1inch_limit"]
        else:
            base_url = blockchain["1inch"]

        self.dex_url = f"{base_url}"
        self.logger.debug("self.dex_url %s", self.dex_url)
        self.logger.debug("self.protocol_type %s", self.protocol_type)

        self.router_contract_addr = router_contract_addr
        if self.router_contract_addr is None:
            self.router_contract_addr = blockchain["uniswap_v2"]

        self.name = "TBD"
        self.logger.debug("self.name %s", self.name)

        self.trading_quote_ccy = settings.trading_quote_ccy
        self.logger.debug("self.trading_quote_ccy %s", self.trading_quote_ccy)

        try:
            self.gecko_api = CoinGeckoAPI()
            assetplatform = self.gecko_api.get_asset_platforms()
            output_dict = [x for x in assetplatform if x['chain_identifier']
                           == int(self.chain_id)]
            self.gecko_platform = output_dict[0]['id']
            self.logger.debug("self.gecko_platform %s", self.gecko_platform)
        except Exception as e:
            self.logger.error("CoinGeckoAPI setup: %s", e)
            return

    async def _get(
                self,
                url,
                params=None,
                headers=None
            ):
        headers = {"User-Agent": "Mozilla/5.0"}
        self.logger.debug("_get url %s", url)
        response = requests.get(
                            url,
                            params=params,
                            headers=headers,
                            timeout=10
                        )
        return response.json()

    async def get_quote(
                self,
                symbol
            ):
        self.logger.debug("get_quote %s", symbol)
        asset_in_address = await self.search_contract(symbol)
        self.logger.debug("asset_in_address %s", asset_in_address)
        asset_out_symbol = self.trading_quote_ccy
        asset_out_address = await self.search_contract(asset_out_symbol)
        self.logger.debug("asset_out_address %s", asset_out_address)
        if asset_out_address is None:
            self.logger.warning("No Valid Contract %s", symbol)
            return
        # asset_out_contract = await self.get_token_contract(asset_out_symbol)
        # asset_out_decimals = asset_out_contract.functions.decimals().call()
        # self.logger.debug(f"asset_out_decimals {asset_out_decimals}")
        try:
            if self.protocol_type == "1inch":
                asset_out_amount = self.w3.to_wei(1, 'ether')
                self.logger.debug("asset_out_amount %s", asset_out_amount)
                quote_url = (self.dex_url
                             + "/quote?fromTokenAddress="
                             + str(asset_in_address)
                             + "&toTokenAddress="
                             + str(asset_out_address)
                             + "&amount="
                             + str(asset_out_amount))
                quote = await self._get(quote_url)
                self.logger.debug("quote %s", quote)
                raw_quote = quote['toTokenAmount']
                self.logger.debug("raw_quote %s", raw_quote)
                asset_quote_decimals = quote['fromToken']['decimals']
                self.logger.debug("asset_quote_decimals %s",
                                  asset_quote_decimals)
                quote_readable = (self.w3.from_wei(int(raw_quote), 'wei') /
                                  (10 ** asset_quote_decimals))
                self.logger.debug("quote_readable %s", quote_readable)
                return round(quote_readable, 2)
            if self.protocol_type in ["uniswap_v2", "uniswap_v3"]:
                return
        except Exception as e:
            self.logger.error("get_quote %s", e)
            return

    async def execute_order(self, order_params):
        """execute swap function"""
        action = order_params.get('action')
        instrument = order_params.get('instrument')
        quantity = order_params.get('quantity', 1)
        try:
            asset_out_symbol = (self.trading_quote_ccy if
                                action == "BUY" else instrument)
            asset_in_symbol = (instrument if action == "BUY"
                               else self.trading_quote_ccy)
            asset_out_contract = await self.get_token_contract(
                asset_out_symbol)
            try:
                asset_out_decimals = (
                    asset_out_contract.functions.decimals().call())
            except Exception as e:
                self.logger.error("execute_order decimals: %s", e)
                asset_out_decimals = 18
            asset_out_balance = await self.get_token_balance(asset_out_symbol)
            #  buy or sell %p percentage DEFAULT OPTION is 10%
            asset_out_amount = ((asset_out_balance) /
                                (settings.trading_risk_amount
                                ** asset_out_decimals)
                                )*(float(quantity)/100)

            order = await self.get_swap(
                    asset_out_symbol,
                    asset_in_symbol,
                    asset_out_amount
                    )
            if order:
                return order['confirmation']

        except Exception as e:
            self.logger.debug("error execute_order %s", e)
            return "error processing order in DXSP"

    async def get_swap(
                self,
                asset_out_symbol: str,
                asset_in_symbol: str,
                amount: int,
                slippage_tolerance_percentage=2
                ):
        """main swap function"""

        self.logger.debug("get_swap")
        try:
            # ASSET OUT
            asset_out_address = await self.search_contract(
                asset_out_symbol)
            asset_out_contract = await self.get_token_contract(
                asset_out_symbol)
            if asset_out_contract is None:
                raise ValueError("No contract identified")
            asset_out_decimals = asset_out_contract.functions.decimals().call()
            asset_out_balance = await self.get_token_balance(asset_out_symbol)
            self.logger.debug("asset_out_balance %s", asset_out_balance)
            if asset_out_balance == 0:
                self.logger.warning("No Money")
                raise ValueError("Non contract identified")
                return
            # ASSETS IN
            asset_in_address = await self.search_contract(asset_in_symbol)
            self.logger.debug("asset_in_address %s", asset_in_address)
            if asset_in_address is None:
                return

            # AMOUNT
            asset_out_decimals = asset_out_contract.functions.decimals().call()
            self.logger.debug("asset_out_decimals %s", asset_out_decimals)
            asset_out_amount = amount * 10 ** asset_out_decimals
            # defaulted to 2% slippage if not given
            slippage = slippage_tolerance_percentage
            self.logger.debug("slippage %s", slippage)
            asset_out_amount_converted = self.w3.to_wei(
                asset_out_amount, 'ether')

            order_amount = int((asset_out_amount_converted * (slippage/100)))
            self.logger.debug("order_amount %s", order_amount)

            # VERIFY IF ASSET OUT IS APPROVED otherwise get it approved
            await self.get_approve(asset_out_address)

            # 1INCH
            if self.protocol_type in ["1inch"]:
                swap_url = (self.dex_url
                            + "/swap?fromTokenAddress="
                            + asset_out_address
                            + "&toTokenAddress="
                            + asset_in_address
                            + "&amount="
                            + order_amount
                            + "&fromAddress="
                            + self.wallet_address
                            + "&slippage="
                            + slippage
                            )
                swap_order = await self._get(swap_url)
                swap_order_status = swap_order['statusCode']
                if swap_order_status != 200:
                    return
            # UNISWAP V2
            if self.protocol_type in ["uniswap_v2"]:
                order_path_dex = [asset_out_address, asset_in_address]
                router_abi = await self.get_abi(self.router_contract_addr)
                router = self.w3.eth.contract(
                                  self.w3.to_checksum_address(
                                    self.router_contract_addr),
                                  router_abi)
                deadline = self.w3.eth.get_block("latest")["timestamp"] + 3600
                order_min_amount = int(router.functions.getAmountsOut(
                                        order_amount,
                                        order_path_dex).call()[1])
                swap_order = router.functions.swapExactTokensForTokens(
                                order_amount,
                                order_min_amount,
                                order_path_dex,
                                self.wallet_address,
                                deadline)
            # 1INCH LIMIT
            if self.protocol_type in ["1inch_limit"]:
                return

            # UNISWAP V3
            if self.protocol_type in ['uniswap_v3']:
                return
            if swap_order:
                self.logger.debug("swap_order %s", swap_order)
                signed_order = await self.get_sign(swap_order)
                order_hash = str(self.w3.to_hex(signed_order))
                order_hash_details = self.w3.wait_for_transaction_receipt(
                                        order_hash,
                                        timeout=120,
                                        poll_latency=0.1)
                if order_hash_details['status'] == "1":
                    await self.get_confirmation(
                        order_hash,
                        order_hash_details,
                        asset_out_symbol,
                        asset_out_address,
                        order_amount,)
        except Exception as e:
            self.logger.error("get_swap %s", e)
            return

    async def get_confirmation(self,
                               order_hash,
                               order_hash_details,
                               asset_out_symbol,
                               asset_out_address,
                               order_amount,
                               ):
        """ trade confirmation function"""
        self.logger.debug("get_confirmation")
        try:
            trade_blockNumber = order_hash_details['blockNumber']
            trade_receipt = self.w3.eth.get_transaction_receipt(order_hash)
            trade_block = self.w3.eth.get_block(trade_blockNumber)
            trade = {}
            trade['id'] = trade_receipt['transactionHash']
            trade['timestamp'] = trade_block['timestamp']
            trade['instrument'] = asset_out_symbol
            trade['contract'] = asset_out_address
            trade['amount'] = order_amount
            trade['fee'] = trade_receipt['gasUsed']
            trade['price'] = "TBD"
            trade['confirmation'] += f"➕ Size: {round(trade['amount'],4)}\n"
            trade['confirmation'] += f"⚫️ Entry: {round(trade['price'],4)}\n"
            trade['confirmation'] += f"ℹ️ {trade['id']}\n"
            trade['confirmation'] += f"🗓️ {trade['datetime']}"
            self.logger.info("trade %s", trade)
            return trade
        except Exception as e:
            self.logger.error("get_confirmation %s", e)
            return

    async def get_block_explorer_status(self, txHash):
        self.logger.debug("get_block_explorer_status %s", txHash)
        checkTransactionSuccessURL = (
            self.block_explorer_url
            + "?module=transaction&action=gettxreceiptstatus&txhash="
            + txHash
            + "&apikey="
            + self.block_explorer_api)
        checkTransactionRequest = self._get(checkTransactionSuccessURL)
        return checkTransactionRequest['status']

# ###CONTRACT SEARCH
    async def search_contract(
                            self,
                            token
                            ):
        """search a contract function"""
        self.logger.debug("search_contract")

        try:
            token_contract = await self.get_contract_address(
                settings.TOKEN_PERSONAL_LIST,
                token)
            if token_contract is None:
                token_contract = await self.get_contract_address(
                    settings.TOKEN_TESTNET_LIST,
                    token)
                if token_contract is None:
                    token_contract = await self.get_contract_address(
                        settings.TOKEN_MAINNET_LIST,
                        token)
                    if token_contract is None:
                        token_contract = await self.search_gecko_contract(
                            token)
            if token_contract is not None:
                self.logger.info("token_contract found %s", token_contract)
                return self.w3.to_checksum_address(token_contract)
            self.logger.info("no contract found for %s", token)
        except Exception as e:
            self.logger.error("search_contract %s", e)
            return

    async def search_gecko(self, token):
        """search coingecko"""
        self.logger.debug("search_gecko")
        try:
            search_results = self.gecko_api.search(query=token)
            search_dict = search_results['coins']
            filtered_dict = [x for x in search_dict if
                             x['symbol'] == token.upper()]
            api_dict = [sub['api_symbol'] for sub in filtered_dict]
            self.logger.debug("api_dict %s", api_dict)
            for i in api_dict:
                coin_dict = self.gecko_api.get_coin_by_id(i)
                try:
                    if coin_dict['platforms'][f'{self.gecko_platform}']:
                        return coin_dict
                except KeyError:
                    pass
        except Exception as e:
            self.logger.error("search_gecko %s", e)
            return

    async def search_gecko_contract(self, token):
        """search coingecko contract"""
        self.logger.debug("🦎search_gecko_contract %s", token)
        self.logger.debug("🦎self.gecko_platform %s", self.gecko_platform)
        try:
            coin_info = await self.search_gecko(token)
            if coin_info is not None:
                return coin_info['platforms'][f'{self.gecko_platform}']
        except Exception as e:
            self.logger.error(f"error search_gecko_contract {e}")
            return

    async def get_contract_address(
                            self,
                            token_list_url,
                            symbol
                        ):
        """Given a token symbol and json format url address tokenlist,
        get token address"""
        self.logger.debug("get_contract_address %s %s", token_list_url, symbol)
        try:
            token_list = await self._get(token_list_url)
            token_search = token_list['tokens']
            for keyval in token_search:
                if (keyval['symbol'] == symbol and
                   keyval['chainId'] == self.chain_id):
                    return keyval['address']
        except Exception as e:
            self.logger.debug("get_contract_address %s", e)
            return

    async def get_token_contract(
                                self,
                                token
                            ):
        """Given a token symbol, returns a contract object. """
        self.logger.debug("get_token_contract %s", token)
        try:
            token_address = await self.search_contract(token)
            token_abi = await self.get_abi(token_address)
            return self.w3.eth.contract(address=token_address, abi=token_abi)
        except Exception as e:
            self.logger.error("get_token_contract %s", e)
            return

# ###UTILS
    async def get_approve(
                        self,
                        asset_out_address: str,
                        amount=None
                    ):
        self.logger.debug("get_approve %s", asset_out_address)
        if self.protocol_type in ["1inch", "1inch_limit"]:
            approval_check_URL = (
                self.dex_url
                + "/approve/allowance?tokenAddress="
                + asset_out_address
                + "&walletAddress="
                + self.wallet_address)
            approval_response = await self._get(approval_check_URL)
            approval_check = approval_response['allowance']
            if (approval_check == 0):
                approval_URL = (
                    self.dex_url
                    + "/approve/transaction?tokenAddress="
                    + asset_out_address)
                approval_response = await self._get(approval_URL)
        elif self.protocol_type in ["uniswap_v2", "uniswap_v3"]:
            asset_out_abi = await self.get_abi(asset_out_address)
            asset_out_contract = self.w3.eth.contract(
                                 asset_out_address,
                                 asset_out_abi)
            approval_check = asset_out_contract.functions.allowance(
                             self.w3.to_checksum_address(self.wallet_address),
                             self.w3.to_checksum_address(
                                self.router_contract_addr)
                             ).call()
            if (approval_check == 0):
                approved_amount = (self.w3.to_wei(2**64-1, 'ether'))
                asset_out_abi = await self.get_abi(asset_out_address)
                asset_out_contract = self.w3.eth.contract(
                                     asset_out_address,
                                     asset_out_abi)
                approval_TX = asset_out_contract.functions.approve(
                                self.w3.to_checksum_address(
                                    self.router_contract_addr),
                                approved_amount)
                approval_txHash = await self.get_sign(approval_TX)
                approval_txHash_complete = (
                    self.w3.eth.wait_for_transaction_receipt(
                        approval_txHash,
                        timeout=120,
                        poll_latency=0.1))
                return approval_txHash_complete

    async def get_sign(
                    self,
                    order
                ):
        self.logger.debug("get_sign %s", order)
        try:
            if not isinstance(order, dict):
                raise ValueError("Transaction must be a dictionary")
            if self.protocol_type in ['uniswap_v2', 'uniswap_v3']:
                order_params = {
                            'from': self.wallet_address,
                            'gas': await self.get_gas(order),
                            'gasPrice': await self.get_gasPrice(order),
                            'nonce': self.w3.eth.get_transaction_count(
                                self.wallet_address),
                            }
                order = order.build_transaction(order_params)
            elif self.protocol_type in ["1inch", "1inch_limit"]:
                order = order['tx']
                order['gas'] = await self.get_gas(order)
                order['nonce'] = self.w3.eth.get_transaction_count(
                    self.wallet_address)
                order['value'] = int(order['value'])
                order['gasPrice'] = await self.get_gasPrice(order)
            signed = self.w3.eth.account.sign_transaction(
                order,
                self.private_key)
            raw_order = signed.rawTransaction
            return self.w3.eth.send_raw_transaction(raw_order)
        except (ValueError, TypeError, KeyError) as e:
            self.logger.error("get_sign: %s", e)
            raise
        except Exception as e:
            self.logger.error("get_sign: %s", e)
            raise RuntimeError("Failed to sign transaction")

    async def get_gas(
                    self,
                    tx
                ):
        # Log the transaction
        self.logger.debug("get_gas %s", tx)
        # Estimate the gas cost of the transaction
        gasestimate = self.w3.eth.estimate_gas(tx) * 1.25
        # Return the estimated gas cost in wei
        return int(self.w3.to_wei(gasestimate, 'wei'))

    async def get_gasPrice(self, tx):
        '''
        Get the gas price for a transaction
        '''
        self.logger.debug("get_gasPrice %s", tx)
        gasprice = self.w3.eth.generate_gas_price()
        return self.w3.to_wei(gasprice, 'gwei')

    async def get_abi(self, addr):
        # Log a debug message to the logger
        self.logger.debug("get_abi %s", addr)
        if self.block_explorer_api:
            try:
                # Create a dictionary of parameters
                params = {
                    "module": "contract",
                    "action": "getabi",
                    "address": addr,
                    "apikey": self.block_explorer_api
                    }
                # Create a dictionary of headers
                headers = {"User-Agent": "Mozilla/5.0"}
                # Make a GET request to the block explorer URL
                resp = await self._get(
                                       url=self.block_explorer_url,
                                       params=params,
                                       headers=headers
                                       )
                # If the response status is 1, log the ABI
                if resp['status'] == "1":
                    self.logger.debug("ABI found %s", resp)
                    abi = resp["result"]
                    return abi
                # If no ABI is identified, log a warning
                self.logger.warning("No ABI identified")
            except Exception as e:
                # Log an error
                self.logger.error("error get_abi %s", e)
                return
        else:
            # If no block_explorer_api is set, log a warning
            self.logger.warning("No block_explorer_api. Option B needed TBD")
            return

# USER BALANCE AND POSITION RELATED

    async def get_token_balance(
                                self,
                                token
                            ):
        self.logger.debug("get_token_balance %s", token)
        try:
            token_address = await self.search_contract(token)
            if token_address is None:
                raise ValueError(f"Token address not found for {token}")
            token_abi = await self.get_abi(token_address)
            if token_abi is None:
                raise ValueError(f"ABI not found for {token_address}")
            token_contract = self.w3.eth.contract(
                token_address,
                token_abi)
            token_balance = 0
            try:
                token_balance = token_contract.functions.balanceOf(
                    self.wallet_address).call()
            except ValueError as e:
                self.logger.warning("Invalid address: %s", e)
            return 0 if token_balance <= 0 else token_balance
        except Exception as e:
            self.logger.error("get_token_balance %s: %s", token, e)
            return 0

    async def get_account_balance(
                            self
                        ):
        try:
            balance = self.w3.eth.get_balance(
                self.w3.to_checksum_address(
                    self.wallet_address))
            balance = (self.w3.from_wei(balance, 'ether'))
            try:
                trading_quote_ccy_balance = (
                    await self.get_trading_quote_ccy_balance())
                if trading_quote_ccy_balance:
                    balance += "💵" + trading_quote_ccy_balance
            except Exception as e:
                self.logger.error("trading_quote_ccy_balance error: %s", e)

            return round(balance, 5)

        except Exception as e:
            self.logger.error("get_account_balance error: %s", e)
            return "balance error"

    async def get_trading_quote_ccy_balance(
                                self
                            ):

        try:
            trading_quote_ccy_balance = await self.get_token_balance(
                settings.trading_quote_ccy)
            if trading_quote_ccy_balance:
                return trading_quote_ccy_balance
            return 0
        except Exception as e:
            self.logger.error("get_trading_quote_ccy_balance error: %s", e)
            return 0

    async def get_account_position(self):
        try:
            self.logger.debug("get_account_position")
            return
        except Exception as e:
            self.logger.error("get_account_position error: %s", e)
            return 0
