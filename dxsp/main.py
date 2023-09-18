"""
 DEX SWAP Main
"""

import decimal
from typing import Optional

from loguru import logger
from web3 import Web3

from dxsp import __version__
from dxsp.config import settings
from dxsp.protocols import DexUniswap, DexZeroX
from dxsp.utils import AccountUtils, ContractUtils


class DexSwap:
    """
    class to build a DexSwap Object
     use to interact with the dex protocol

     Args:
         w3 (Optional[Web3]): Web3

     Returns:
         DexSwap


    """

    def __init__(self, w3: Optional[Web3] = None):
        """
        Initialize the DexTrader object
        to interact with exchanges

        """
        exchanges = settings.dex
        self.dex_info = []
        self.commands = settings.dxsp_commands
        try:
            for dx in exchanges:
                logger.debug(f"Loading {dx}")
                name = dx
                wallet_address = exchanges[dx]["wallet_address"]
                private_key = exchanges[dx]["private_key"]
                w3 = Web3(Web3.HTTPProvider(exchanges[dx]["rpc"]))
                protocol_type = exchanges[dx]["protocol_type"]
                protocol_version = exchanges[dx]["protocol_version"]
                api_endpoint = exchanges[dx]["api_endpoint"]
                api_key = exchanges[dx]["api_key"]
                router_contract_addr = exchanges[dx]["router_contract_addr"]
                factory_contract_addr = exchanges[dx]["factory_contract_addr"]
                trading_asset_address = exchanges[dx]["trading_asset_address"]
                trading_risk_amount = exchanges[dx]["trading_risk_amount"]
                trading_slippage = exchanges[dx]["trading_slippage"]
                block_explorer_url = exchanges[dx]["block_explorer_url"]
                block_explorer_api = exchanges[dx]["block_explorer_api"]
                client = self._create_client(
                    name=name,
                    wallet_address=wallet_address,
                    private_key=private_key,
                    w3=w3,
                    protocol_type=protocol_type,
                    protocol_version=protocol_version,
                    api_endpoint=api_endpoint,
                    api_key=api_key,
                    router_contract_addr=router_contract_addr,
                    factory_contract_addr=factory_contract_addr,
                    trading_asset_address=trading_asset_address,
                    trading_risk_amount=trading_risk_amount,
                    trading_slippage=trading_slippage,
                    block_explorer_url=block_explorer_url,
                    block_explorer_api=block_explorer_api,
                )
                # if protocol_type == "uniswap":
                #     client = DexUniswap(
                #         name=name,
                #         wallet_address=wallet_address,
                #         private_key=private_key,
                #         w3=w3,
                #         protocol_type=protocol_type,
                #         protocol_version=protocol_version,
                #         api_endpoint=api_endpoint,
                #         api_key=api_key,
                #         router_contract_addr=router_contract_addr,
                #         factory_contract_addr=factory_contract_addr,
                #         trading_asset_address=trading_asset_address,
                #         trading_risk_amount=trading_risk_amount,
                #         trading_slippage=trading_slippage,
                #         block_explorer_url=block_explorer_url,
                #         block_explorer_api=block_explorer_api,
                #     )
                # if protocol_type == "0x":
                #     client = DexZeroX(
                #         name=name,
                #         wallet_address=wallet_address,
                #         private_key=private_key,
                #         w3=w3,
                #         protocol_type=protocol_type,
                #         protocol_version=protocol_version,
                #         api_endpoint=api_endpoint,
                #         api_key=api_key,
                #         router_contract_addr=router_contract_addr,
                #         factory_contract_addr=factory_contract_addr,
                #         trading_asset_address=trading_asset_address,
                #         trading_risk_amount=trading_risk_amount,
                #         trading_slippage=trading_slippage,
                #         block_explorer_url=block_explorer_url,
                #         block_explorer_api=block_explorer_api,
                #     )
                self.dex_info.append(client)
            logger.debug("init complete")

        except Exception as e:
            logger.error(e)

    def _create_client(self, **kwargs):
        protocol_type = kwargs["protocol_type"]
        if protocol_type == "uniswap":
            return DexUniswap(**kwargs)
        elif protocol_type == "0x":
            return DexZeroX(**kwargs)
        else:
            raise ValueError(f"Unsupported protocol type: {protocol_type}")

    async def get_quote(self, sell_token):
        """
        gets a quote for a token

        Args:
            sell_token (str): The sell token.

        Returns:
            str: The quote with the trading symbol

        """
        logger.debug("get quote", sell_token)
        info = "🦄\n"
        for dx in self.dex_info:
            logger.debug("get quote {}", dx)
            buy_address = dx.trading_asset_address
            sell_address = await dx.contract_utils.search_contract_address(sell_token)
            quote = await dx.get_quote(buy_address, sell_address) or "Quote failed"
            symbol = await dx.contract_utils.get_token_symbol(dx.trading_asset_address)
            info += f"{dx.name}: {quote} {symbol}\n"

        return info.strip()

    async def get_swap(
        self, dex_client, sell_token: str, buy_token: str, quantity: int
    ) -> None:
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
            sell_token_address = sell_token
            logger.debug("sell token {}", sell_token_address)
            if not sell_token.startswith("0x"):
                sell_token_address = (
                    await dex_client.contract_utils.search_contract_address(sell_token)
                )
            buy_token_address = buy_token
            logger.debug("buy token {}", buy_token_address)
            if not buy_token_address.startswith("0x"):
                buy_token_address = (
                    await dex_client.contract_utils.search_contract_address(buy_token)
                )

            sell_amount = await dex_client.contract_utils.calculate_sell_amount(
                sell_token_address, dex_client.account.wallet_address, quantity
            )
            sell_token_amount_wei = sell_amount * (
                10 ** (await dex_client.account.get_token_decimals(sell_token_address))
            )
            if dex_client.protocol_type == "0x":
                await dex_client.account.get_approve(sell_token_address)

            order_amount = int(
                sell_token_amount_wei
                * decimal.Decimal((dex_client.trading_slippage / 100))
            )
            logger.debug(order_amount)
            order = await dex_client.get_swap(
                sell_token_address, buy_token_address, order_amount
            )

            if not order:
                logger.debug("swap order error")
                raise ValueError("swap order not executed")

            signed_order = await dex_client.account.get_sign(order)
            order_hash = str(dex_client.w3.to_hex(signed_order))
            receipt = dex_client.w3.wait_for_transaction_receipt(order_hash)

            if receipt["status"] != 1:
                logger.debug(receipt)
                raise ValueError("receipt failed")

            return await dex_client.account.get_confirmation(receipt["transactionHash"])

        except Exception as error:
            logger.debug(error)
            raise error

    async def execute_order(self, order_params):
        """
        Execute an order function.

        Args:
            order_params (dict): The order parameters.

        Returns:
            str: The trade confirmation

        """
        try:
            for dx in self.dex_info:
                logger.debug("execute order {}", dx)
                action = order_params.get("action")
                instrument = order_params.get("instrument")
                quantity = order_params.get("quantity", 1)
                sell_token, buy_token = (
                    (dx["trading_asset_address"], instrument)
                    if action == "BUY"
                    else (instrument, dx["trading_asset_address"])
                )
                order = await self.get_swap(dx, sell_token, buy_token, quantity)
                if order:
                    trade_confirmation = (
                        f"⬇️ {instrument}"
                        if (action == "SELL")
                        else f"⬆️ {instrument}\n"
                    )
                    trade_confirmation += order
                    return trade_confirmation

        except Exception as error:
            return f"⚠️ order execution: {error}"

    async def get_help(self):
        """
        Get the help information for the current instance.
        Returns:
            A string containing the available commands.
        """
        return f"{self.commands}\n"

    async def get_info(self):
        """
        Get information from the account.

        :return: The information retrieved from the account.
        """
        info = "ℹ️  v{__version__}\n"
        for dx in self.dex_info:
            info += await dx.get_info() or "Info failed\n"
        return info.strip()

    async def get_name(self):
        """
        Retrieves the name of the account.

        :return: The name of the account.
        """
        info = ""
        for dx in self.dex_info:
            info += await dx.get_name() or "Name failed"
        return info.strip()

    # 🔒 USER RELATED
    async def get_account_balance(self):
        """
        Retrieves the account balance.

        :return: The account balance.
        :rtype: float
        """
        info = ""
        for dx in self.dex_info:
            info += await dx.get_account_balance() or "Account balance failed"
        return info.strip()

    async def get_trading_asset_balance(self):
        """
        Retrieves the trading asset balance for the current account.

        :return: A dictionary containing the trading asset balance.
                 The dictionary has the following keys:
                 - 'asset': The asset symbol.
                 - 'free': The free balance of the asset.
                 - 'locked': The locked balance of the asset.
        """
        info = ""
        for dx in self.dex_info:
            info += (
                await dx.get_trading_asset_balance() or "Trading asset balance failed"
            )
        return info.strip()

    async def get_account_position(self):
        """
        Retrieves the account position.

        :return: The account position.
        :rtype: AccountPosition
        """
        info = ""
        for dx in self.dex_info:
            info += await dx.get_account_position() or "Account position failed"
        return info.strip()

    async def get_account_margin(self):
        """
        Retrieves the account margin.

        :return: The account margin.
        :rtype: float
        """
        info = ""
        for dx in self.dex_info:
            info += await dx.get_account_margin() or "Account margin failed"
        return info.strip()

    async def get_account_open_positions(self):
        """
        Retrieves the open positions of the account.

        :return: A list of open positions in the account.
        """
        info = ""
        for dx in self.dex_info:
            info += (
                await dx.get_account_open_positions() or "Account open positions failed"
            )
        return info.strip()

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
        info = ""
        for dx in self.dex_info:
            info += (
                await dx.get_account_transactions(period)
                or "Account transactions failed"
            )
        return info.strip()

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
        info = ""
        for dx in self.dex_info:
            info += await dx.get_account_pnl(period) or "Account PnL failed"
        return info.strip()
 