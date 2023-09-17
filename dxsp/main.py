"""
 DEX SWAP Main
"""

import decimal
from typing import Optional

from loguru import logger
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy

from dxsp.config import settings
from dxsp.protocols.client import DexClient
from dxsp.utils import AccountUtils, ContractUtils


class DexTrader:
    """
    DEXswap  class to build a DexSwap Object
    use to interact with the dex protocol

    Args:
        w3 (Optional[Web3]): Web3

    Returns:
        DexSwap


    """

    def __init__(self, w3: Optional[Web3] = None):
        """
        Initialize the DexSwap object to interact with
        w3 contracts.

        """
        exchanges = settings.dex
        self.dex_info = []
        try:
            self.commands = settings.dxsp_commands
            for cx in exchanges:
                logger.debug(f"Loading {cx}")
                w3 = w3 or Web3(Web3.HTTPProvider(exchanges[cx]["rpc"]))
                protocol_type = exchanges[cx]["protocol_type"]
                protocol_version= exchanges[cx]["protocol_version"]
                api_endpoint= exchanges[cx]["api_endpoint"]
                api_key= exchanges[cx]["api_key"]
                router= exchanges[cx]["router_contract_addr"]
                trading_asset_address= exchanges[cx]["trading_asset_address"]
                block_explorer_url= exchanges[cx]["block_explorer_url"]
                block_explorer_api= exchanges[cx]["block_explorer_api"]
                account_utils= AccountUtils(w3)
                contract_utils= ContractUtils(w3)
                gas_strategy= w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
                client = DexClient(w3=w3,
                                   protocol_type=protocol_type,
                                   protocol_version=protocol_version,
                                   api_endpoint=api_endpoint,
                                   api_key=api_key,
                                   router=router,
                                   trading_asset_address=trading_asset_address,
                                   block_explorer_url=block_explorer_url,
                                   block_explorer_api=block_explorer_api)
                self.dex_info.append(
                    {
                        "w3": w3,
                        "protocol_type": protocol_type,
                        "protocol_version": protocol_version,
                        "api_endpoint": api_endpoint,
                        "api_key": api_key,
                        "router": router,
                        "client": client,
                        "trading_asset_address": trading_asset_address,
                        "block_explorer_url": block_explorer_url,
                        "block_explorer_api": block_explorer_api,
                        "account_utils": account_utils,
                        "contract_utils": contract_utils,
                        "gas_strategy": gas_strategy
                    }
                )

        except Exception as e:
            logger.error(e)

    async def execute_order(self, order_params):
        """
        Execute an order function.

        Args:
            order_params (dict): The order parameters.

        Returns:
            str: The trade confirmation

        """
        try:
            for exchange in self.dex_info:
                logger.debug("execute order")
                action = order_params.get("action")
                instrument = order_params.get("instrument")
                quantity = order_params.get("quantity", 1)
                sell_token, buy_token = (
                    (self.account.trading_asset_address, instrument)
                    if action == "BUY"
                    else (instrument, self.account.trading_asset_address)
                )
                order = await self.get_swap(sell_token, buy_token, quantity)
                if order:
                    trade_confirmation = (
                        f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
                    )
                    trade_confirmation += order
                    return trade_confirmation

        except Exception as error:
            return f"⚠️ order execution: {error}"


    async def get_swap(self, sell_token: str, buy_token: str, quantity: int) -> None:
        """
        Execute a swap

        Args:
            sell_token (str): The sell token.
            buy_token (str): The buy token.
            quantity (int): The quantity of tokens.

        Returns:
            transactionHash


        """
        try:

            logger.debug("get swap")
            await self.get_protocol()
            sell_token_address = sell_token
            logger.debug("sell token {}", sell_token_address)
            if not sell_token.startswith("0x"):
                sell_token_address = await self.contract_utils.search_contract_address(
                    sell_token
                )
            buy_token_address = buy_token
            logger.debug("buy token {}", buy_token_address)
            if not buy_token_address.startswith("0x"):
                buy_token_address = await self.contract_utils.search_contract_address(
                    buy_token
                )
            sell_amount = await self.contract_utils.calculate_sell_amount(
                sell_token_address, self.account.wallet_address, quantity
            )
            sell_token_amount_wei = sell_amount * (
                10 ** (await self.contract_utils.get_token_decimals(sell_token_address))
            )
            if self.protocol_type == "0x":
                await self.account.get_approve(sell_token_address)

            order_amount = int(
                sell_token_amount_wei
                * decimal.Decimal((settings.dex_trading_slippage / 100))
            )
            logger.debug(order_amount)
            order = await self.dex_swap.get_swap(
                sell_token_address, buy_token_address, order_amount
            )

            if not order:
                logger.debug("swap order error")
                raise ValueError("swap order not executed")

            signed_order = await self.account.get_sign(order)
            order_hash = str(self.w3.to_hex(signed_order))
            receipt = self.w3.wait_for_transaction_receipt(order_hash)

            if receipt["status"] != 1:
                logger.debug(receipt)
                raise ValueError("receipt failed")

            return await self.contract_utils.get_confirmation(
                receipt["transactionHash"]
            )

        except Exception as error:
            logger.debug(error)
            raise error

    async def get_quote(self, sell_token):
        """
        gets a quote for a token

        Args:
            sell_token (str): The sell token.

        Returns:
            str: The quote with the trading symbol

        """
        try:
            for cx in self.dex_info:
                buy_address = cx["trading_asset_address"]
                sell_address = await cx["contract_utils"](sell_token)
                quote = await cx["client"].get_quote(buy_address, sell_address)
                quote = f"🦄 {quote}"
                symbol = await cx["contract_utils"].get_token_symbol(
                    cx["trading_asset_address"]
                )
                return f"{quote} {symbol}"

        except Exception as error:
            return f"⚠️: {error}"

    # 🔒 USER RELATED

    async def get_info(self):
        """
        Get information from the account.

        :return: The information retrieved from the account.
        """
        info = ""
        for item in self.dex_info:
            info += await item["account_utils"].get_info()
        return info.strip()


    async def get_help(self):
        """
        Get the help information for the current instance.

        Returns:
            A string containing the available commands.
        """
        return f"{self.commands}\n"

    async def get_name(self):
        """
        Retrieves the name of the account.

        :return: The name of the account.
        """
        return await self.account.get_name()

    async def get_account_balance(self):
        """
        Retrieves the account balance.

        :return: The account balance.
        :rtype: float
        """
        return await self.account.get_account_balance()

    async def get_trading_asset_balance(self):
        """
        Retrieves the trading asset balance for the current account.

        :return: A dictionary containing the trading asset balance.
                 The dictionary has the following keys:
                 - 'asset': The asset symbol.
                 - 'free': The free balance of the asset.
                 - 'locked': The locked balance of the asset.
        """
        return await self.account.get_trading_asset_balance()

    async def get_account_position(self):
        """
        Retrieves the account position.

        :return: The account position.
        :rtype: AccountPosition
        """
        return await self.account.get_account_position()

    async def get_account_margin(self):
        """
        Retrieves the account margin.

        :return: The account margin.
        :rtype: float
        """
        return await self.account.get_account_margin()

    async def get_account_open_positions(self):
        """
        Retrieves the open positions of the account.

        :return: A list of open positions in the account.
        """
        return await self.account.get_account_open_positions()

    async def get_account_transactions(self, period=24):
        """
        Get the account transactions
        for a specific period.

        Args:
            period (int): The number of hours
            for which to retrieve the transactions. Defaults to 24.

        Returns:
            List[Transaction]: A list of
            transaction objects representing the account transactions.
        """
        return await self.account.get_account_transactions(period)

    async def get_account_pnl(self, period=24):
        """
        Get the profit and loss (PnL)
        for the account within a specified period.

        Args:
            period (int, optional):
            The period in hours for which to calculate the PnL.
            Defaults to 24.

        Returns:
            float: The profit and loss (PnL)
            for the account within the specified period.
        """
        return await self.account.get_account_pnl(period)

