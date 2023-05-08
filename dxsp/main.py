"""
 DEX SWAP Main
"""

import logging

import requests
from dxsp import __version__
from dxsp.config import settings

from pycoingecko import CoinGeckoAPI
from web3 import Web3


class DexSwap:
    """Do a swap."""

    def __init__(self, w3: Web3 | None = None,):
        """build a dex object """
        self.logger = logging.getLogger(name="DexSwap")
        self.logger.info("DexSwap: %s", __version__)

        self.w3 = w3 or Web3(Web3.HTTPProvider(settings.dex_rpc))
        try:
            if self.w3.net.listening:
                self.logger.info("connected %s", self.w3)
        except Exception as e:
            self.logger.error("connectivity failed %s", e)
            return

        self.protocol_type = settings.dex_protocol_type
        self.chain_id = settings.dex_chain_id
        # USER
        self.wallet_address = settings.dex_wallet_address
        self.private_key = settings.dex_private_key

        # COINGECKO
        try:
            self.cg = CoinGeckoAPI()
            assetplatform = self.cg.get_asset_platforms()
            output_dict = [x for x in assetplatform if x['chain_identifier']
                           == int(self.chain_id)]
            self.cg_platform = output_dict[0]['id']
            self.logger.debug("cg_platform %s", self.cg_platform)
        except Exception as e:
            self.logger.error("CoinGecko: %s", e)
            return

    async def _get(
        self,
        url,
        params=None,
        headers=None
            ):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10)
        return response.json()

    async def router(self):
        try:
            router_abi = await self.get_abi(settings.dex_router_contract_addr)
            router = self.w3.eth.contract(
                self.w3.to_checksum_address(
                    settings.dex_router_contract_addr),
                router_abi)
            return router
        except Exception as e:
            self.logger.error("router setup: %s", e)
            return

    async def get_quote(
                self,
                symbol
            ):
        self.logger.debug("get_quote %s", symbol)
        asset_in_address = await self.search_contract(symbol)
        asset_out_symbol = settings.trading_quote_ccy
        asset_out_address = await self.search_contract(asset_out_symbol)
        if asset_out_address is None:
            self.logger.warning("No Valid Contract %s", symbol)
            return
        try:
            if self.protocol_type in ["1inch", "1inch_limit"]:
                await self.oneinch_quote(
                    asset_in_address,
                    asset_out_address)
            if self.protocol_type == "uniswap_v2":
                await self.uniswap_v2_quote(
                    asset_in_address,
                    asset_out_address)
            if self.protocol_type == "uniswap_v3":
                await self.uniswap_v3_quote(
                    asset_in_address,
                    asset_out_address)
        except Exception as e:
            self.logger.error("get_quote %s", e)
            return

    async def oneinch_quote(
        self,
        asset_in_address,
        asset_out_address,
        amount=1
    ):
        try:
            asset_out_amount = self.w3.to_wei(amount, 'ether')
            quote_url = (
                settings.dex_base_api
                + "/quote?fromTokenAddress="
                + str(asset_in_address)
                + "&toTokenAddress="
                + str(asset_out_address)
                + "&amount="
                + str(asset_out_amount))
            quote_response = await self._get(quote_url)
            self.logger.debug("quote %s", quote_response)
            quote_amount = quote_response['toTokenAmount']
            quote_decimals = quote_response['fromToken']['decimals']
            quote = (
                self.w3.from_wei(int(quote_amount), 'wei') /
                (10 ** quote_decimals))
            self.logger.debug("quote %s", quote)
            return round(quote, 2)
        except Exception as e:
            self.logger.error("oneinch_quote %s", e)
            return

    async def uniswap_v2_quote(
        self,
        asset_in_address,
        asset_out_address,
        amount=1
    ):
        try:
            order_path_dex = [asset_out_address, asset_in_address]
            router_instance = await self.router()
            order_min_amount = int(
                router_instance.functions.getAmountsOut(
                    amount,
                    order_path_dex)
                .call()[1])
            return order_min_amount
        except Exception as e:
            self.logger.error("uniswap_v2_quote %s", e)
            return

    async def uniswap_v3_quote(
        self,
        asset_in_address,
        asset_out_address,
        amount=1
    ):
        return

    async def execute_order(self, order_params):
        """execute swap function"""
        action = order_params.get('action')
        instrument = order_params.get('instrument')
        quantity = order_params.get('quantity', 1)

        try:
            asset_out_symbol = (
                settings.trading_quote_ccy if
                action == "BUY" else instrument)
            asset_in_symbol = (
                instrument if action == "BUY"
                else settings.trading_quote_ccy)
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
            asset_out_amount = (
                (asset_out_balance) /
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
            asset_out_balance = await self.get_token_balance(asset_out_symbol)
            if asset_out_balance == 0:
                self.logger.warning("No Money")
                raise ValueError("No Money")
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
            asset_out_amount_converted = self.w3.to_wei(
                asset_out_amount, 'ether')

            order_amount = int(
                (asset_out_amount_converted *
                 (settings.slippage/100)))
            self.logger.debug("order_amount %s", order_amount)

            # VERIFY IF ASSET OUT IS APPROVED otherwise get it approved
            await self.get_approve(asset_out_address)

            # 1INCH
            if self.protocol_type in ["1inch"]:
                swap_order = await self.oneinch_swap(
                    asset_out_address,
                    asset_in_address,
                    order_amount)
            # UNISWAP V2
            if self.protocol_type in ["uniswap_v2"]:
                swap_order = await self.uniswap_v2_swap(
                    asset_out_address,
                    asset_in_address,
                    order_amount)
            # 1INCH LIMIT
            if self.protocol_type in ["1inch_limit"]:
                return
            # UNISWAP V3
            if self.protocol_type in ['uniswap_v3']:
                swap_order = await self.uniswap_v3_swap()
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

    async def oneinch_swap(
        self,
        asset_out_address,
        asset_in_address,
        amount
    ):
        swap_url = (settings.dex_base_api
                    + "/swap?fromTokenAddress="
                    + asset_out_address
                    + "&toTokenAddress="
                    + asset_in_address
                    + "&amount="
                    + amount
                    + "&fromAddress="
                    + self.wallet_address
                    + "&slippage="
                    + settings.slippage
                    )
        swap_order = await self._get(swap_url)
        swap_order_status = swap_order['statusCode']
        if swap_order_status != 200:
            return
        return swap_order

    async def uniswap_v2_swap(
        self,
        asset_out_address,
        asset_in_address,
        amount
    ):
        order_path_dex = [asset_out_address, asset_in_address]

        deadline = self.w3.eth.get_block("latest")["timestamp"] + 3600
        order_min_amount = self.uniswap_v2_quote(
            asset_in_address,
            asset_out_address)
        router_instance = await self.router()
        swap_order = router_instance.functions.swapExactTokensForTokens(
                        amount,
                        order_min_amount,
                        order_path_dex,
                        self.wallet_address,
                        deadline)
        return swap_order

    async def uniswap_v3_swap(self):
        self.logger.warning("Not available")
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
        if settings.block_explorer_api:
            self.logger.debug("get_block_explorer_status %s", txHash)
            checkTransactionSuccessURL = (
                settings.block_explorer_url
                + "?module=transaction&action=gettxreceiptstatus&txhash="
                + str(txHash)
                + "&apikey="
                + str(settings.block_explorer_api))
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
                settings.token_personal_list,
                token)
            if token_contract is None:
                token_contract = await self.get_contract_address(
                    settings.token_testnet_list,
                    token)
                if token_contract is None:
                    token_contract = await self.get_contract_address(
                        settings.token_mainnet_list,
                        token)
                    if token_contract is None:
                        token_contract = await self.search_cg_contract(
                            token)
            if token_contract is not None:
                self.logger.info("token_contract found %s", token_contract)
                return self.w3.to_checksum_address(token_contract)
            self.logger.info("no contract found for %s", token)
        except Exception as e:
            self.logger.error("search_contract %s", e)
            return

    async def search_cg(self, token):
        """search coingecko"""
        self.logger.debug("search_cg")
        try:
            search_results = self.cg.search(query=token)
            search_dict = search_results['coins']
            filtered_dict = [x for x in search_dict if
                             x['symbol'] == token.upper()]
            api_dict = [sub['api_symbol'] for sub in filtered_dict]
            self.logger.debug("api_dict %s", api_dict)
            for i in api_dict:
                coin_dict = self.cg.get_coin_by_id(i)
                try:
                    if coin_dict['platforms'][f'{self.cg_platform}']:
                        return coin_dict
                except KeyError:
                    pass
        except Exception as e:
            self.logger.error("search_cg %s", e)
            return

    async def search_cg_contract(self, token):
        """search coingecko contract"""
        self.logger.debug("🦎search_cg_contract %s", token)
        try:
            coin_info = await self.search_cg(token)
            if coin_info is not None:
                return coin_info['platforms'][f'{self.cg_platform}']
        except Exception as e:
            self.logger.error(" search_cg_contract: %s", e)
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
            return self.w3.eth.contract(
                address=token_address,
                abi=token_abi)
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
                settings.dex_base_api
                + "/approve/allowance?tokenAddress="
                + str(asset_out_address)
                + "&walletAddress="
                + str(self.wallet_address))
            approval_response = await self._get(approval_check_URL)
            approval_check = approval_response['allowance']
            if (approval_check == 0):
                approval_URL = (
                    settings.dex_base_api
                    + "/approve/transaction?tokenAddress="
                    + str(asset_out_address))
                approval_response = await self._get(approval_URL)
        elif self.protocol_type in ["uniswap_v2", "uniswap_v3"]:
            asset_out_abi = await self.get_abi(asset_out_address)
            asset_out_contract = self.w3.eth.contract(
                                 address=asset_out_address,
                                 abi=asset_out_abi)
            approval_check = asset_out_contract.functions.allowance(
                             self.w3.to_checksum_address(self.wallet_address),
                             self.w3.to_checksum_address(
                                settings.dex_router_contract_addr)
                             ).call()
            if (approval_check == 0):
                approved_amount = (self.w3.to_wei(2**64-1, 'ether'))
                asset_out_abi = await self.get_abi(asset_out_address)
                asset_out_contract = self.w3.eth.contract(
                                     address=asset_out_address,
                                     abi=asset_out_abi)
                approval_TX = asset_out_contract.functions.approve(
                                self.w3.to_checksum_address(
                                    settings.router_contract_addr),
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
                settings.dex_private_key)
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
        if settings.dex_block_explorer_api:
            try:
                # Create a dictionary of parameters
                params = {
                    "module": "contract",
                    "action": "getabi",
                    "address": addr,
                    "apikey": settings.dex_block_explorer_api
                    }
                # Create a dictionary of headers
                headers = {"User-Agent": "Mozilla/5.0"}
                # Make a GET request to the block explorer URL
                resp = await self._get(
                                       url=settings.dex_block_explorer_url,
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
            self.logger.warning("No block_explorer_api.")
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
                address=token_address,
                abi=token_abi)
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
