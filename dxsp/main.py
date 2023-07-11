"""
 DEX SWAP Main
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
import requests
from pycoingecko import CoinGeckoAPI
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy
from dxsp import __version__
from dxsp.config import settings


class DexSwap:
    """swap  class"""
    def __init__(self, w3: Optional[Web3] = None):
        self.logger = logging.getLogger(name="DexSwap")
        self.w3 = w3 or Web3(Web3.HTTPProvider(settings.dex_rpc))
        if self.w3.net.listening:
            self.logger.info("connected %s", self.w3)
            self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
            self.chain_id = self.w3.net.version
            self.wallet_address = self.w3.to_checksum_address(
                settings.dex_wallet_address)
            self.account = (f"{str(self.w3.net.version)} - "
                            f"{str(self.wallet_address[-8:])}")
            self.private_key = settings.dex_private_key
            self.trading_asset_address = self.w3.to_checksum_address(
                settings.trading_asset_address)

            self.protocol_type = settings.dex_protocol_type
            self.protocol_version = settings.dex_protocol_version
            self.dex_swap = None
            self.router = None
            self.quoter = None
        else:
            raise ValueError("w3 not connected")

        self.cg = CoinGeckoAPI()

    async def get_protocol(self):
        """ protocol init """
        from dxsp.protocols import DexSwapUniswap, DexSwapZeroX, DexSwapOneInch
        if self.protocol_type == "0x":
            self.dex_swap = DexSwapZeroX()
        elif self.protocol_type == "1inch":
            self.dex_swap = DexSwapOneInch()
        else:
            self.dex_swap = DexSwapUniswap()

    async def execute_order(self, order_params):
        """ Execute swap function. """
        try:
            action = order_params.get('action')
            instrument = order_params.get('instrument')
            quantity = order_params.get('quantity', 1)
            sell_token, buy_token = (
                (self.trading_asset_address, instrument)
                if action == 'BUY'
                else (instrument, self.trading_asset_address))
            order = await self.get_swap(sell_token, buy_token, quantity)
            if order:
                trade_confirmation = (
                    f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n")
                trade_confirmation += order
                return trade_confirmation

        except Exception as error:
            return f"⚠️ order execution: {error}"

    async def get_swap(self, sell_token: str, buy_token: str, quantity: int) -> None:
        """ Main swap function """
        try:
            await self.get_protocol()
            sell_token_address = sell_token
            if not sell_token.startswith("0x"):
                sell_token_address = await self.search_contract_address(sell_token)
            buy_token_address = buy_token
            if not buy_token_address.startswith("0x"):
                buy_token_address = await self.search_contract_address(buy_token)
            sell_amount = await self.calculate_sell_amount(sell_token_address, quantity)
            sell_token_amount_wei = sell_amount * (10 ** (
                await self.get_token_decimals(sell_token_address)))
            await self.get_approve(sell_token_address)

            order_amount = int(
                sell_token_amount_wei * (settings.dex_trading_slippage / 100))
            order = await self.dex_swap.get_swap(
                sell_token_address, buy_token_address, order_amount)

            if not order:
                raise ValueError("swap order not executed")

            signed_order = await self.get_sign(order)
            order_hash = str(self.w3.to_hex(signed_order))
            receipt = self.w3.wait_for_transaction_receipt(order_hash)

            if receipt["status"] != 1:
                raise ValueError("receipt failed")

            return await self.get_confirmation(receipt['transactionHash'])

        except ValueError as error:
            raise error

    async def get_quote(self, sell_token):
        """ gets a quote for a token """
        try:
            await self.get_protocol()
            buy_address = self.trading_asset_address
            sell_address = await self.search_contract_address(sell_token)
            quote = await self.dex_swap.get_quote(buy_address, sell_address)
            # settings to be reviewed and removed
            # TODO
            return f"🦄 {quote} {settings.trading_asset}"
        except Exception as error:
            return f"⚠️: {error}"

    async def get_approve(self, token_address):
        """ approve a token """
        try:
            contract = await self.get_token_contract(token_address)
            if contract is None:
                return
            approved_amount = self.w3.to_wei(2 ** 64 - 1, 'ether')
            owner_address = self.w3.to_checksum_address(self.wallet_address)
            dex_router_address = self.w3.to_checksum_address(
                settings.dex_router_contract_addr)
            allowance = contract.functions.allowance(
                owner_address, dex_router_address).call()
            if allowance == 0:
                approval_tx = contract.functions.approve(
                    dex_router_address, approved_amount)
                approval_tx_hash = await self.get_sign(approval_tx.transact())
                return self.w3.eth.wait_for_transaction_receipt(
                    approval_tx_hash)
        except Exception as error:
            raise ValueError(f"Approval failed {error}")

    async def get_sign(self, transaction):
        """ sign a transaction """
        try:
            if self.protocol_type == 'uniswap':
                transaction_params = {
                    'from': self.wallet_address,
                    'gas': await self.get_gas(transaction),
                    'gasPrice': await self.get_gas_price(),
                    'nonce': self.w3.eth.get_transaction_count(
                        self.wallet_address),
                }
                transaction = transaction.build_transaction(transaction_params)
            signed_tx = self.w3.eth.account.sign_transaction(
                transaction, self.private_key)
            raw_tx_hash = self.w3.eth.send_raw_transaction(
                signed_tx.rawTransaction)
            return self.w3.to_hex(raw_tx_hash)
        except Exception as error:
            raise error

# ------🛠️ W3 UTILS ---------
    async def get(self, url, params=None, headers=None):
        """ gets a url payload """
        try:
            self.logger.debug(f"Requesting URL: {url}")
            response = requests.get(
                url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()

        except Exception as error:
            raise error

    async def calculate_sell_amount(self, sell_token_address, quantity):
        """Returns amount based on risk percentage."""
        sell_balance = await self.get_token_balance(sell_token_address)
        sell_contract = await self.get_token_contract(sell_token_address)
        sell_decimals = (sell_contract.functions.decimals().call() 
        if sell_contract is not None else 18)
        risk_percentage = settings.trading_risk_amount
        return (sell_balance / 
        (risk_percentage * 10 ** sell_decimals)) * (float(quantity) / 100)

    async def get_confirmation(self, transactionHash):
        """Returns trade confirmation."""
        try:
            transaction = self.w3.eth.get_transaction(transactionHash)
            block = self.w3.eth.get_block(transaction["blockNumber"])
            return {
                "timestamp": block["timestamp"],
                "id": transactionHash,
                "instrument": transaction["to"],
                "contract": transaction["to"],   # TBD To be determined.
                "amount": transaction["value"],
                "price": transaction["value"],  # TBD To be determined.
                "fee": transaction["gas"],
                "confirmation": (
                    f"➕ Size: {round(transaction['value'], 4)}\n"
                    f"⚫️ Entry: {round(transaction['value'], 4)}\n"
                    f"ℹ️ {transactionHash}\n"
                    f"⛽ {transaction['gas']}\n"
                    f"🗓️ {block['timestamp']}"
                ),
            }
        except Exception as error:
            raise error

    async def get_gas(self, transaction):
        """get gas estimate"""
        gas_limit = self.w3.eth.estimate_gas(transaction) * 1.25
        return int(self.w3.to_wei(gas_limit, 'wei'))

    async def get_gas_price(self):
        """search get gas price"""
        return round(self.w3.from_wei(self.w3.eth.generate_gas_price(), 'gwei'), 2)

    async def get_block_timestamp(self, block_num) -> datetime:
            """Get block timestamp"""
            block_info = self.w3.eth.get_block(block_num)
            last_time = block_info["timestamp"]
            return datetime.utcfromtimestamp(last_time)

# ## ------✍️ CONTRACT ---------
    async def search_contract_address(self, token):
        """search a contract function"""

        contract_lists = [
            settings.token_personal_list,
            settings.token_testnet_list,
            settings.token_mainnet_list,
        ]
        for contract_list in contract_lists:
            token_address = await self.get_token_address(
                contract_list,
                token
            )
            if token_address is not None:
                return self.w3.to_checksum_address(token_address)

        token_address = await self.search_cg_contract(token)
        if token_address is None:
            if settings.dex_notify_invalid_token:
                raise ValueError("Invalid Token")
            return
        return self.w3.to_checksum_address(token_address)

    async def search_cg_platform(self):
        """search coingecko platform"""
        asset_platforms = self.cg.get_asset_platforms()
        output_dict = next(
            x for x in asset_platforms
            if x["chain_identifier"] == int(self.chain_id)
        )
        return output_dict["id"] or None

    async def search_cg(self, token):
        """search coingecko"""
        try:
            search_results = self.cg.search(query=token)
            search_dict = search_results['coins']
            filtered_dict = [x for x in search_dict if
                             x['symbol'] == token.upper()]
            api_dict = [sub['api_symbol'] for sub in filtered_dict]
            for i in api_dict:
                coin_dict = self.cg.get_coin_by_id(i)
                try:
                    if coin_dict['platforms'][f'{await self.search_cg_platform()}']:
                        return coin_dict
                except (KeyError, requests.exceptions.HTTPError):
                    pass
        except Exception as e:
            self.logger.error("search_cg %s", e)
            return

    async def search_cg_contract(self, token):
        """search coingecko contract"""
        try:
            coin_info = await self.search_cg(token)
            return (coin_info['platforms'][f'{await self.search_cg_platform()}']
                    if coin_info is not None else None)
        except Exception as e:
            self.logger.error(" search_cg_contract: %s", e)
            return

    async def get_token_address(self, token_list_url, symbol):
        """Given a token symbol and json tokenlist, get token address"""
        token_list = await self.get(token_list_url)
        token_search = token_list['tokens']
        for keyval in token_search:
            if (keyval['symbol'] == symbol and
                keyval['chainId'] == self.chain_id):
                return keyval['address']

    async def get_token_contract(self, token_address):
        """Given a token address, returns a contract object. """
        token_abi = await self.get_explorer_abi(token_address)
        if token_abi is None:
            token_abi = await self.get(settings.dex_erc20_abi_url)
        return self.w3.eth.contract(
            address=token_address,
            abi=token_abi)

    async def get_token_decimals(self, token_address: str) -> Optional[int]:
        """Get token decimals"""
        contract = await self.get_token_contract(token_address)
        return 18 if not contract else contract.functions.decimals().call()

    async def get_token_symbol(self, token_address: str):
        """Get token symbol"""
        contract = await self.get_token_contract(token_address)
        #token_name = contract.functions.name().call()
        return contract.functions.symbol().call() 


    async def get_token_balance(self, token_address: str) -> Optional[int]:
        """Get token balance"""
        contract = await self.get_token_contract(token_address)
        if contract is None or contract.functions is None:
            raise ValueError("No Balance")
        balance = contract.functions.balanceOf(self.wallet_address).call()
        if balance is None:
            raise ValueError("No Balance")
        return round(balance,5)

    async def get_explorer_abi(self, address):
        if not settings.dex_block_explorer_api:
            return None

        params = {
            "module": "contract",
            "action": "getabi",
            "address": address,
            "apikey": settings.dex_block_explorer_api
        }
        resp = await self.get(
            url=settings.dex_block_explorer_url, params=params)
        if resp['status'] == "1":
            self.logger.debug("ABI found %s", resp)
            return resp["result"]
        else:
            return None

# 🔒 USER RELATED
    async def get_info(self):
        return (f"ℹ️ {__class__.__name__} {__version__}\n"
                f"💱 {await self.get_name()}\n"
                f"🪪 {self.account}")

    async def get_name(self):
        if settings.dex_router_contract_addr:
            return settings.dex_router_contract_addr[-8:]
        else:
            return self.protocol_type

    async def get_account_balance(self):
        account_balance = self.w3.eth.get_balance(
            self.w3.to_checksum_address(self.wallet_address))
        account_balance = self.w3.from_wei(account_balance, 'ether') or 0
        trading_asset_balance = await self.get_trading_asset_balance() or 0
        return f"₿ {round(account_balance,5)}\n💵 {trading_asset_balance}"

    async def get_trading_asset_balance(self):
        trading_asset_balance = await self.get_token_balance(
            self.trading_asset_address)
        return trading_asset_balance if trading_asset_balance else 0

    async def get_account_position(self):
        position = "📊 Position\n"
        position += f"Opened: {str(await self.get_account_open_positions())}/n"
        position += f"Margin: {str(await self.get_account_margin())}"
        return position

    async def get_account_margin(self):
        return 0

    async def get_account_open_positions(self):
        return 0

    async def get_account_pnl(self, period=24):
        """
        Create a profit and loss (PnL) 
        report for the account.
        """
        pnl_dict = await self.get_account_transactions(period)
        pnl_report = "".join(
            f"{token} {value}\n" for token, value in pnl_dict["tokenList"].items()
        )
        pnl_report += f"Total {pnl_dict['pnl']}\n"
        pnl_report += await self.get_account_position()

        return pnl_report

    async def get_account_transactions(self, period=24):
        """
        Retrieves the account transactions 
        within a specified time period
        for the main asset activity
        """
        pnl_dict = {"pnl": 0, "tokenList": {}}
        if not settings.dex_block_explorer_api:
            return pnl_dict
    
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": self.trading_asset_address,
            "address": self.wallet_address,
            "page": "1",
            "offset": "100",
            "startblock": "0",
            "endblock": "99999999",
            "sort": "desc",
            "apikey": settings.dex_block_explorer_api
        }
    
        response = await self.get(
            url=settings.dex_block_explorer_url, params=params)
    
        if response.get('status') == "1" and "result" in response:
            current_time = datetime.utcnow()
            time_history_start = current_time - timedelta(hours=period)
    
            for entry in response["result"]:
                token_symbol = entry.get("tokenSymbol")
                value = int(entry.get("value", 0))
                timestamp = int(entry.get("timeStamp", 0))
                transaction_time = datetime.utcfromtimestamp(timestamp)
    
                if transaction_time >= time_history_start and token_symbol:
                    pnl_dict["tokenList"][token_symbol] = (
                    pnl_dict["tokenList"].get(token_symbol, 0) + value)
                    pnl_dict["pnl"] += value
    
        return pnl_dict
