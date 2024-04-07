"""
Base DexClient Class   🦄
"""

import decimal

from loguru import logger
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware

from dxsp.utils import AccountUtils, ContractUtils


class DexClient:
    """
    Base DexClient Class

    Args:
        **kwargs:

    Returns:
        None

    Methods:
        resolve_buy_token
        resolve_sell_token
        resolve_token
        replace_instrument
        get_order_amount
        get_quote
        get_swap
        make_swap
        get_account_balance
        get_trading_asset_balance
        get_account_position
        get_account_margin
        get_account_open_positions
        get_account_pnl

    """

    def __init__(self, **kwargs):

        self.name = kwargs.get("name", None)
        logger.debug(f"Setting up: {self.name}")

        self.protocol = kwargs.get("protocol") or "uniswap"
        self.protocol_version = kwargs.get("protocol_version") or 2
        self.api_endpoint = kwargs.get("api_endpoint", None)
        self.api_key = kwargs.get("api_key", None)
        self.rpc = kwargs.get("rpc", None)
        self.w3 = Web3(Web3.HTTPProvider(self.rpc))
        if self.w3:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
            logger.debug("Chain hex {}", self.w3.net.version)
            logger.debug("Chain {}", int(self.w3.net.version, 16))

        self.wallet_address = kwargs.get("wallet_address", None)
        self.private_key = kwargs.get("private_key", None)
        if self.w3 and self.wallet_address:
            self.account_number = (
                f"{int(self.w3.net.version, 16)} - {str(self.wallet_address)[-8:]}"
            )
        else:
            self.account_number = None
        logger.debug("Account {}", self.account_number)

        self.router_contract_addr = kwargs.get("router_contract_addr", None)
        self.factory_contract_addr = kwargs.get("factory_contract_addr", None)
        self.trading_asset_address = kwargs.get("trading_asset_address", None)
        self.trading_risk_percentage = kwargs.get("trading_risk_percentage", None)
        self.trading_asset_separator = kwargs.get("trading_asset_separator", None)
        self.trading_risk_amount = kwargs.get("trading_risk_amount", None)
        self.trading_slippage = kwargs.get("trading_slippage", None)
        self.trading_amount_threshold = kwargs.get("trading_amount_threshold", None)
        self.block_explorer_url = kwargs.get("block_explorer_url", None)
        self.block_explorer_api = kwargs.get("block_explorer_api", None)
        self.mapping = kwargs.get("mapping", None)

        self.contract_utils = ContractUtils(
            self.w3, self.block_explorer_url, self.block_explorer_api
        )
        self.account = AccountUtils(
            self.w3,
            self.contract_utils,
            self.wallet_address,
            self.private_key,
            self.trading_asset_address,
            self.block_explorer_url,
            self.block_explorer_api,
        )
        self.client = None

    async def resolve_token(self, **kwargs):
        """
        A function to resolve a token based on the input address or symbol.
        It takes *args and **kwargs as input parameters.
        Returns the data associated with the token.

        Args:
            **kwargs: either an address or a symbol.

        Returns:
            Token: The token object containing the data if contract_address is provided.
            None: If neither symbol nor contract_address is provided.
        """
        logger.debug("Resolving token {}", kwargs)
        try:
            (identifier,) = kwargs.values()
        except ValueError as e:
            raise ValueError(
                "Token identification must be an address or a symbol"
            ) from e

        # Determine if the input is an address or a symbol
        # Assuming addresses start with '0x'
        if identifier.startswith("0x"):
            result = await self.contract_utils.get_data(contract_address=identifier)
        else:
            symbol = await self.replace_instrument(identifier)
            result = await self.contract_utils.get_data(symbol=symbol)

        # Check if the result is not None
        if not result:
            raise ValueError("Token {} not found", identifier)

        return result

    async def replace_instrument(self, instrument):
        """
        Replace instrument by an alternative instrument, if the
        instrument is not in the mapping, it will be ignored.
        Mapping, define in settings as TOML or .env variable.
        It is a list of dictionaries such as:
        mapping = [
            { id = "BTC", alt = "WBTC" ,enable = true },
        ]

        Args:
            instrument (str):

        Returns:
            dict
        """
        logger.debug("Replace instrument: {}", instrument)
        if self.mapping is None:
            return instrument
        for item in self.mapping:
            if item["id"] == instrument:  # and item["enable"] is not False:
                instrument = item["alt"]
                logger.debug("Instrument symbol changed {}", instrument)
                break
        logger.debug("Instrument symbol changed {}", instrument)
        return instrument

    async def get_order_amount(
        self, sell_token, wallet_address, quantity, is_percentage=True
    ):
        """
        Calculate the order amount based on the sell token,
        wallet address, quantity, and whether it is a percentage.

        Args:
            sell_token (SellToken): The sell token object.
            wallet_address (str): The wallet address.
            quantity (float): The quantity of the sell token.
            is_percentage (bool, optional):
            Flag indicating whether the quantity is a percentage. Defaults to True.

        Returns:
            float: The calculated order amount.
        """
        logger.debug("get order amount {} {} {}", sell_token, wallet_address, quantity)
        logger.debug("Protocol", self.contract_utils.platform)
        balance = await sell_token.get_token_balance(wallet_address)
        logger.debug("Balance {}", balance)
        if not is_percentage and balance:
            logger.debug("Quantity {}", quantity)
            return quantity

        if balance:
            risk_percentage = float(quantity) / 100
            logger.debug("Risk percentage {}", risk_percentage)
            amount = balance * decimal.Decimal(risk_percentage)
            logger.debug("Amount {}", amount)
            if (
                isinstance(amount, decimal.Decimal)
                and amount > self.trading_amount_threshold
            ):
                logger.debug("Amount {}", amount)
                return amount

        return 0

    async def get_quote(
        self,
        buy_address=None,
        buy_symbol=None,
        sell_address=None,
        sell_symbol=None,
        amount=1,
    ):
        """
        Get a quote method for specific protocol

        """

    async def get_swap(self, sell_token=None, buy_token=None, quantity=1):
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
            logger.debug("get swap {} {} {}", sell_token, buy_token, quantity)
            logger.debug("Protocol", self.contract_utils.platform)
            sell_token = await self.contract_utils.get_data(symbol=sell_token)
            logger.debug("sell token {}", sell_token)
            buy_token = await self.contract_utils.get_data(symbol=buy_token)
            logger.debug("buy token {}", buy_token)

            sell_amount = await self.get_order_amount(
                sell_token, self.account.wallet_address, quantity
            )
            if not sell_amount:
                logger.error("sell amount {}", sell_amount)
                return f"⚠️ sell amount failed {sell_amount}"

            sell_token_amount_wei = decimal.Decimal(sell_amount) * (
                decimal.Decimal("10") ** int(sell_token.decimals)
            )
            if self.protocol == "0x":
                await self.account.get_approve(sell_token.address)

            order_amount = int(
                sell_token_amount_wei * decimal.Decimal((self.trading_slippage / 100))
            )
            logger.debug("order amount {}", order_amount)

            order = await self.make_swap(
                sell_token.address, buy_token.address, order_amount
            )

            if not order:
                logger.error("swap order not executed")
                return "⚠️ order execution failed"

            signed_order = await self.account.get_sign(order)
            order_hash = str(self.w3.to_hex(signed_order))
            logger.debug(order_hash)
            receipt = self.w3.eth.wait_for_transaction_receipt(order_hash)
            logger.debug(receipt)

            if receipt["status"] != 1:
                logger.error("receipt failed")

            return await self.account.get_confirmation(receipt["transactionHash"])

        except Exception as error:
            logger.debug(error)
            raise error

    async def make_swap(self, sell_address, buy_address, amount):
        """
        Make a swap method for specific protocol

        """

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

    async def get_account_pnl(self):
        """
        Return account pnl.

        Args:
            None

        Returns:
            pnl
        """

        return await self.account.get_account_pnl()
