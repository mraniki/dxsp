"""
0️⃣x

"""

from loguru import logger

from dxsp.utils.utils import fetch_url

from ._client import DexClient


class ZeroxHandler(DexClient):
    """
    A DexClient class using 0x protocol
    Implementation of 0x swap protocol
    https://0x.org/docs/0x-swap-api/introduction

    """

    def __init__(
        self,
        **kwargs,
    ):
        """
        Initialize the client

        """
        super().__init__(**kwargs)
        self.client = "0x"

    async def get_quote(
        self,
        buy_address=None,
        buy_symbol=None,
        sell_address=None,
        sell_symbol=None,
        amount=1,
    ):
        """
        Retrieves a quote for a token swap.

        Args:
            buy_address (str): The address of the token to be bought.
            sell_address (str): The address of the token to be sold.
            amount (int, optional): The amount of tokens to be sold. Defaults to 1.

        Returns:
            float: The guaranteed price for the token swap.
        """
        try:
            logger.debug(
                "0x get_quote {} {} {} {}",
                buy_address,
                buy_symbol,
                sell_address,
                sell_symbol,
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
            if not buy_token or not sell_token:
                return "⚠️ Buy or sell token not found"
            amount_wei = amount * (10 ** (sell_token.decimals))

            url = (
                f"{self.api_endpoint}/swap/v1/quote"
                f"?buyToken={buy_token.address}&sellToken={sell_token.address}&sellAmount={amount_wei}"
            )
            logger.debug("0x get_quote url {}", url)

            headers = {"0x-api-key": self.api_key}
            response = await fetch_url(url, params=None, headers=headers)
            logger.debug("0x get_quote response {}", response)
            if response:
                if "guaranteedPrice" in response:
                    return float(response["guaranteedPrice"])
                elif "code" in response and "reason" in response:
                    return response["code"], response["reason"]
        except Exception as error:
            logger.error("Quote failed {}", error)
            return f"⚠️ {error}"

    async def make_swap(self, buy_address, sell_address, amount):
        """
        Asynchronously gets a swap order by calling the `get_quote`
        method with the specified `buy_address`,
        `sell_address`, and `amount` parameters.
        Then, it calls the `get_sign` method of the
        `account` object, passing the `swap_order`
        as an argument, and returns the result.

        :param buy_address: The buy address for the swap.
        :param sell_address: The sell address for the swap.
        :param amount: The amount for the swap.

        :return: The result of calling the `get_sign` method
        of the `account` object with the `swap_order`
        as an argument.
        """
        try:
            logger.debug(f"0x make_swap {buy_address} {sell_address} {amount}")
            swap_order = await self.get_quote(buy_address, sell_address, amount)
            if swap_order:
                return await self.account.get_sign(swap_order)

        except Exception as error:
            logger.error("Swap failed {}", error)
            return f"⚠️ {error}"
