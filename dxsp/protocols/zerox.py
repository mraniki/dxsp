"""
0️⃣x

"""
from loguru import logger

from dxsp.protocols import DexClient
from dxsp.utils.utils import get


class DexZeroX(DexClient):
    """
    A DexClient class using 0x protocol
    Implementation of 0x swap protocol
    https://0x.org/docs/0x-swap-api/introduction

    """

    async def get_quote(self, buy_address=None, symbol=None, amount=1):
        """
        Retrieves a quote for a token swap.

        Args:
            buy_address (str): The address of the token to be bought.
            sell_address (str): The address of the token to be sold.
            amount (int, optional): The amount of tokens to be sold. Defaults to 1.

        Returns:
            float: The guaranteed price for the token swap.
        """
        if buy_address is None:
            buy_address = self.trading_asset_address
        sell_address = str(await self.get_instrument_address(symbol))
        logger.debug(f"0x quote {buy_address} {sell_address} {amount}")
        token_decimals = await self.contract_utils.get_token_decimals(sell_address)
        logger.debug("token_decimals {}", token_decimals)
        out_amount = str(amount * (10**token_decimals))
        logger.debug("out_amount {}", out_amount)
        url = (
            f"{self.api_endpoint}/swap/v1/quote"
            f"?buyToken={buy_address}&sellToken={sell_address}&sellAmount={out_amount}"
        )
        logger.debug("0x quote url {}", url)
        headers = {"0x-api-key": self.api_key}
        response = await get(url, params=None, headers=headers)
        logger.debug("0x quote response {}", response)
        if response:
            if "guaranteedPrice" in response:
                return float(response["guaranteedPrice"])
            elif "code" in response and "reason" in response:
                return response["code"], response["reason"]
            else:
                return "Error from 0x"

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
        logger.debug(f"0x swap {buy_address} {sell_address} {amount}")
        swap_order = await self.get_quote(buy_address, sell_address, amount)
        return await self.account.get_sign(swap_order)
