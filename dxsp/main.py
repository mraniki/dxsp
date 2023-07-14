"""
 DEX SWAP Main
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
import decimal
import requests
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy
from dxsp import __version__
from dxsp.config import settings
from dxsp.utils import ContractUtils, AccountUtils


class DexSwap:
    """swap  class"""
    def __init__(self, w3: Optional[Web3] = None):
        self.logger = logging.getLogger(name="DexSwap")
        self.w3 = w3 or Web3(Web3.HTTPProvider(settings.dex_rpc))
        if not self.w3.net.listening:
            raise ValueError("w3 not connected")
        self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
        # self.chain_id = self.w3.net.version
        # self.wallet_address = self.w3.to_checksum_address(
        #     settings.dex_wallet_address)
        # self.account = (f"{str(self.w3.net.version)} - "
        #                 f"{str(self.wallet_address[-8:])}")
        # self.private_key = settings.dex_private_key
        # self.trading_asset_address = self.w3.to_checksum_address(
        #     settings.trading_asset_address)

        self.account = AccountUtils(w3=self.w3)

        self.protocol_type = settings.dex_protocol_type
        self.protocol_version = settings.dex_protocol_version
        self.dex_swap = None
        self.router = None
        self.quoter = None
        self.contract_utils = ContractUtils(w3=self.w3)

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
                (self.account.trading_asset_address, instrument)
                if action == 'BUY'
                else (instrument, self.account.trading_asset_address))
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
            print("get_swap", quantity)
            await self.get_protocol()
            sell_token_address = sell_token
            if not sell_token.startswith("0x"):
                sell_token_address = await self.contract_utils.search_contract_address(sell_token)
            buy_token_address = buy_token
            if not buy_token_address.startswith("0x"):
                buy_token_address = await self.contract_utils.search_contract_address(buy_token)
            sell_amount = await self.calculate_sell_amount(sell_token_address, quantity)
            sell_token_amount_wei = sell_amount * (10 ** (
                await self.get_token_decimals(sell_token_address)))
            if self.protocol_type == "0x":
                await self.get_approve(sell_token_address)

            order_amount = int(
                sell_token_amount_wei * decimal.Decimal(
                    (settings.dex_trading_slippage / 100)))
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
            buy_address = self.account.trading_asset_address
            sell_address = await self.contract_utils.search_contract_address(sell_token)
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
            owner_address = self.w3.to_checksum_address(self.account.wallet_address)
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
                    'from': self.account.wallet_address,
                    'gas': await self.get_gas(transaction),
                    'gasPrice': await self.get_gas_price(),
                    'nonce': self.w3.eth.get_transaction_count(
                        self.account.wallet_address),
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
        sell_decimals = (
            sell_contract.functions.decimals().call()
            if sell_contract is not None else 18)
        risk_percentage = settings.trading_risk_amount
        return ((sell_balance / (risk_percentage * 10 ** sell_decimals))
                * (decimal.Decimal(quantity)/ 100)) 


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

# 🔒 USER RELATED
    async def get_info(self):
        return await self.account.get_info()

    async def get_name(self):
        return await self.account.get_name()

    async def get_account_balance(self):
        return await self.account.get_account_balance()

    async def get_trading_asset_balance(self):
        return await self.account.get_trading_asset_balance()

    async def get_account_position(self):
        return await self.account.get_account_position()

    async def get_account_margin(self):
        return await self.account.get_account_margin()

    async def get_account_open_positions(self):
        return await self.account.get_account_open_positions()

    async def get_account_pnl(self, period=24):
        """
        Create a profit and loss (PnL) 
        report for the account.
        """
        return await self.account.get_account_pnl()

    async def get_account_transactions(self, period=24):
        """
        Retrieves the account transactions 
        within a specified time period
        for the main asset activity
        """
        return await self.account.get_account_transactions(period)