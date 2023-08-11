"""
0️⃣x

"""
from dxsp.config import settings
from dxsp.main import DexSwap
from dxsp.utils.utils import get


class DexSwapZeroX(DexSwap):
    """
    A DEXSwap sub class using 0x protocol
    Implementation of 0x swap protocol
    https://0x.org/docs/0x-swap-api/introduction

    """

    async def get_quote(self, buy_address, sell_address, amount=1):
        """
        Retrieves a quote for a token swap.

        Args:
            buy_address (str): The address of the token to be bought.
            sell_address (str): The address of the token to be sold.
            amount (int, optional): The amount of tokens to be sold. Defaults to 1.

        Returns:
            float: The guaranteed price for the token swap.
        """
        token_decimals = await self.contract_utils.get_token_decimals(sell_address)
        out_amount = amount * (10**token_decimals)
        url = (
            f"{settings.dex_0x_url}/swap/v1/quote"
            f"?buyToken={str(buy_address)}&sellToken={str(sell_address)}&sellAmount={str(out_amount)}"
        )
        headers = {"0x-api-key": settings.dex_0x_api_key}
        response = await get(url, params=None, headers=headers)
        if response:
            return float(response["guaranteedPrice"])

    async def get_swap(self, buy_address, sell_address, amount):
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
        swap_order = await self.get_quote(buy_address, sell_address, amount)
        return await self.account.get_sign(swap_order)
