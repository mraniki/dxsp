"""
uniswap  🦄
"""

from loguru import logger
from uniswap import Uniswap

from ._client import DexClient


class UniswapHandler(DexClient):
    """
    A DexClient using uniswap-python library

    More info on uniswap-python library:
    https://github.com/uniswap-python/uniswap-python

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
        self.build_client()

    def build_client(self):
        """
        Initializes the Uniswap object.

        Parameters:
            None

        Returns:
            None
        """
        try:
            logger.debug(
                "Uniswap client starting. RPC: {}",
                self.rpc,
            )
            self.client = Uniswap(
                address=self.wallet_address,
                private_key=self.private_key,
                version=self.protocol_version,
                provider=self.rpc,
                web3=self.w3,
                factory_contract_addr=self.factory_contract_addr,
                router_contract_addr=self.router_contract_addr,
            )
            logger.debug("Uniswap client {}", self.client)
        except Exception as error:
            logger.error("Uniswap client failed {}", error)
            raise Exception("Uniswap client creation failed, Verify rpc")

    async def get_quote(
        self,
        buy_address=None,
        buy_symbol=None,
        sell_address=None,
        sell_symbol=None,
        amount=1,
    ):
        """
        Retrieves a quote for a given buy and sell token pair.

        :param buy_address: The address of the buy token. Default is None.
        :param buy_symbol: The symbol of the buy token. Default is None.
        :param sell_address: The address of the sell token. Default is None.
        :param sell_symbol: The symbol of the sell token. Default is None.
        :param amount: The amount of tokens to buy. Default is 1.

        :return: The price of the buy token in terms of the sell token.
        :rtype: float

        :raises Exception: If the quote retrieval fails.
        """

        try:

            logger.debug(
                f"Uniswap get_quote: {buy_symbol} to {sell_symbol}, "
                f"buy={buy_address}, sell={sell_address}"
            )
            # Resolve buy_token
            buy_token = await self.resolve_token(
                address_or_symbol=buy_address
                or buy_symbol
                or self.trading_asset_address
            )

            # Resolve sell_token
            sell_token = await self.resolve_token(
                address_or_symbol=sell_address or sell_symbol
            )
            logger.debug("Buy token {}. Sell token {}", buy_token, sell_token)

            if not buy_token or not sell_token:
                return "⚠️ Buy or sell token not found"
            amount_wei = amount * (10 ** (sell_token.decimals))

            logger.debug(
                f"Buy Token Address: {buy_token.address}\n"
                f"Sell Token Address: {sell_token.address}\n"
                f"Amount in Wei: {amount_wei}"
            )
            quote = self.client.get_price_input(
                sell_token.address, buy_token.address, amount_wei
            )
            logger.debug("Quote {}", quote)
            if quote is None:
                return "Quote failed"
            quote_amount = quote / (10**buy_token.decimals)
            logger.debug("Quote amount {}", quote_amount)
            return round(float(quote_amount), 5)

        except Exception as error:
            logger.error("Quote failed {}", error)
            return f"⚠️ {error}"

    async def make_swap(self, sell_address, buy_address, amount):
        """
        Make a swap on Uniswap.

        Args:
            sell_address (str): The address of the token to sell.
            buy_address (str): The address of the token to buy.
            amount (float): The amount of tokens to swap.

        Returns:
            object: The result of the swap.

        Raises:
            Exception: If the swap fails.
        """

        try:

            logger.debug(
                "Uniswap make_swap {} {} {}", sell_address, buy_address, amount
            )
            return self.client.make_trade(sell_address, buy_address, amount)

        except Exception as error:
            logger.error("Swap failed {}", error)
            return f"⚠️ {error}"

    # async def calculate_pnl(self, period=None):
    #     """
    #     Calculate the PnL for a given period.

    #     Parameters:
    #         period (str):
    #         The period for which to calculate PnL ('W', 'M', 'Y', or None)

    #     Returns:
    #         pnl: The calculated PnL value.
    #     """
    #     # TODO: implement this
    #     # return await self.account.get_account_pnl()
