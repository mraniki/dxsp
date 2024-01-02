"""
Base DexClient Class   🦄
"""

import decimal

from loguru import logger
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware

from dxsp.utils import AccountUtils, ContractUtils


class DexClient:
    """
    Base DexClient Class

    Args:
        name (str): The name of the dex
        wallet_address (str): The wallet address
        private_key (str): The private key
        protocol (str): The protocol type
        protocol_version (int): The protocol version
        api_endpoint (str): The api endpoint
        api_key (str): The api key
        router_contract_addr (str): The router contract address
        factory_contract_addr (str): The factory contract address
        trading_asset_address (str): The trading asset address
        trading_risk_amount (int): The trading risk amount
        trading_slippage (int): The trading slippage
        block_explorer_url (str): The block explorer url
        block_explorer_api (str): The block explorer api
        w3 (Optional[Web3]): Web3


    """

    def __init__(
        self,
        w3=None,
        rpc=None,
        name=None,
        wallet_address=None,
        private_key=None,
        protocol=None,
        protocol_version=None,
        api_endpoint=None,
        api_key=None,
        router_contract_addr=None,
        factory_contract_addr=None,
        trading_asset_address=None,
        trading_asset_separator=None,
        trading_risk_percentage=True,
        trading_risk_amount=1,
        trading_slippage=2,
        trading_amount_threshold=0,
        block_explorer_url=None,
        block_explorer_api=None,
        mapping=None,
    ):
        self.w3 = w3
        # Add the Geth POA Middleware
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        # Set gas price strategy
        self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
        # Add caching middlewares
        #self.w3.middleware_onion.add(middleware.time_based_cache_middleware)
        #self.w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        #self.w3.middleware_onion.add(middleware.simple_cache_middleware)


        self.rpc = rpc
        self.name = name
        logger.debug(f"setting up DexClient: {self.name}")
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.account_number = (
            f"{int(self.w3.net.version, 16)} - " f"{str(self.wallet_address)[-8:]}"
        )
        logger.debug("account number {}", self.account_number)
        logger.debug("chain hex {}", self.w3.net.version)
        logger.debug("chain {}", int(self.w3.net.version, 16))
        self.protocol = protocol
        self.protocol_version = int(protocol_version)
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.router_contract_addr = router_contract_addr
        self.factory_contract_addr = factory_contract_addr
        self.trading_asset_address = self.w3.to_checksum_address(trading_asset_address)
        self.trading_risk_percentage = trading_risk_percentage
        self.trading_asset_separator = trading_asset_separator
        self.trading_risk_amount = trading_risk_amount
        self.trading_slippage = trading_slippage
        self.trading_amount_threshold = trading_amount_threshold
        self.block_explorer_url = block_explorer_url
        self.block_explorer_api = block_explorer_api
        self.mapping = mapping

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

    async def resolve_buy_token(self, buy_address=None, buy_symbol=None):
        if buy_address:
            return await self.contract_utils.get_data(contract_address=buy_address)
        elif buy_symbol:
            buy_symbol = await self.replace_instrument(buy_symbol)
            return await self.contract_utils.get_data(symbol=buy_symbol)
        else:
            raise ValueError("Buy symbol or address is required.")

    async def resolve_sell_token(self, sell_address=None, sell_symbol=None):
        if sell_address:
            return await self.contract_utils.get_data(contract_address=sell_address)
        elif sell_symbol:
            sell_symbol = await self.replace_instrument(sell_symbol)
            return await self.contract_utils.get_data(symbol=sell_symbol)
        else:
            return await self.contract_utils.get_data(
                contract_address=self.trading_asset_address)

    async def resolve_token(self, address=None, symbol=None, default_address=None):
        if address:
            return await self.contract_utils.get_data(contract_address=address)
        elif symbol:
            symbol = await self.replace_instrument(symbol)
            return await self.contract_utils.get_data(symbol=symbol)
        elif default_address:
            return await self.contract_utils.get_data(contract_address=default_address)
        else:
            raise ValueError("Token symbol or address is required.")


    async def replace_instrument(self, instrument):
        """
        Replace instrument by an alternative instrument, if the
        instrument is not in the mapping, it will be ignored.

        Args:
            order (dict):

        Returns:
            dict
        """
        logger.debug("Replace instrument: {}", instrument)
        if self.mapping is None:
            return instrument
        for item in self.mapping:
            if item["id"] == instrument:
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
