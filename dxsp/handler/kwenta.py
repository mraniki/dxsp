"""
Kwenta 🧮

"""

from kwenta import Kwenta
from loguru import logger

from ._client import DexClient


class KwentaHandler(DexClient):
    """
    A DexClient using kwenta-python library

    More info
    https://github.com/Kwenta/kwenta-python-sdk

    """

    def __init__(
        self,
        **kwargs,
    ):
        """
        Initialize the client

        """
        super().__init__(**kwargs)
        if self.rpc is None or self.w3 is None:
            return
        self.client = Kwenta(
            network_id=int(self.w3.net.version),
            provider_rpc=self.rpc,
            wallet_address=self.wallet_address,
            private_key=self.private_key,
        )

    async def get_quote(
        self,
        buy_address=None,
        buy_symbol=None,
        sell_address=None,
        sell_symbol=None,
        amount=1,
    ):
        """
        Retrieves a quote for a given symbol.

        Args:
            buy_address (str, optional): The buy address. Defaults to None.
            symbol (str, optional): The symbol to retrieve the quote for.
            Defaults to None.
            amount (int, optional): The amount of the asset to retrieve the quote for.
            Defaults to 1.

        Returns:
            float: The quote for the specified symbol.

        Raises:
            Exception: If an error occurs during the retrieval process.
        """
        try:
            buy_token = await self.resolve_token(
                address_or_symbol=buy_address
                or buy_symbol
                or self.trading_asset_address
            )
            sell_token = await self.resolve_token(
                address_or_symbol=sell_address or sell_symbol
            )

            if not buy_token or not sell_token:
                return "⚠️ Buy or sell token not found"

            market = self.client.markets[f"{sell_token.symbol}"]
            logger.info("market: {}", market)
            quote = self.client.get_current_asset_price(sell_token.symbol)
            logger.info("quote: {}", quote)
            return quote or "⚠️ Quote failed"
        except Exception as error:
            logger.error("Quote failed {}", error)
            return f"⚠️ {error}"

    async def make_swap(self, sell_address, buy_address, amount):
        pass

        # symbol = self.contract_utils.get_token_symbol(buy_address)
        # logger.debug(f"Symbol: {symbol}\n")
        # # get the market info for the asset
        # market = self.client.markets[symbol]
        # logger.debug(f"Market: {market}\n")

        # # check margin balance
        # margin_balance_before = self.client.get_accessible_margin(symbol)
        # logger.debug(f"Starting margin balance: {margin_balance_before}\n")

        # # transfer margin to the market
        # transfer_margin = self.client.transfer_margin(symbol, 100, execute_now=True)
        # logger.debug(f"Transfer tx: {transfer_margin}\n")

        # # wait for the transfer to be mined
        # self.client.web3.eth.wait_for_transaction_receipt(transfer_margin)
        # logger.debug("Transfer transaction confirmed\n")
        # await asyncio.sleep(10)

        # # check margin balance again
        # margin_balance_after = self.client.get_accessible_margin(symbol)
        # logger.debug(f"Ending margin balance: {margin_balance_after}\n")

        # # submit an order
        # open_position = self.client.modify_position(
        # symbol,
        # size_delta=0.5,
        # execute_now=True)
        # logger.debug(f"Open position tx: {open_position}\n")

        # # wait for the transfer to be mined
        # self.client.web3.eth.wait_for_transaction_receipt(open_position)
        # logger.debug("Order transaction confirmed\n")
        # await asyncio.sleep(2)

        # # check the order status
        # order_before = self.client.check_delayed_orders(symbol)
        # logger.debug(f"Order before: {order_before}\n")
        # await asyncio.sleep(20)

        # # check the open position
        # position = self.client.get_current_position(symbol)
        # logger.debug(f"Position: {position}\n")

        # # check the order status again
        # order_after = self.client.check_delayed_orders(symbol)
        # logger.debug(f"Order after: {order_after}\n")
