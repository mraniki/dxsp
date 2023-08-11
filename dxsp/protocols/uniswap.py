"""
uniswap  🦄
"""
from uniswap import Uniswap

from dxsp.config import settings
from dxsp.main import DexSwap


class DexSwapUniswap(DexSwap):
    """
    A DEXSwap sub class using uniswap-python library

    More info on uniswap-python library:
    https://github.com/uniswap-python/uniswap-python

    """

    async def get_quote(self, buy_address, sell_address, amount=1):
        """
        Retrieves a quote for the given buy and sell addresses.

        Args:
            buy_address (str): The address of the token to buy.
            sell_address (str): The address of the token to sell.
            amount (int, optional): The amount of tokens to sell. Defaults to 1.

        Returns:
            float: The calculated quote for the given buy and sell addresses.
        """
        try:
            uniswap = Uniswap(
                address=self.account.wallet_address,
                private_key=self.account.private_key,
                version=self.protocol_version,
                web3=self.w3,
                factory_contract_addr=settings.dex_factory_contract_addr,
                router_contract_addr=settings.dex_router_contract_addr,
            )
            amount_wei = amount * (
                10 ** (await self.contract_utils.get_token_decimals(sell_address))
            )
            quote = uniswap.get_price_input(sell_address, buy_address, amount_wei)
            return round(
                float(
                    (
                        quote
                        / (
                            10
                            ** (
                                await self.contract_utils.get_token_decimals(
                                    buy_address
                                )
                            )
                        )
                    )
                ),
                5,
            )

        except Exception as error:
            raise ValueError(f"Quote failed {error}")

    async def get_swap(self, sell_address, buy_address, amount):
        """
        Asynchronously gets the swap
        for the specified sell address, buy address, and amount.

        :param sell_address: The address of the token being sold.
        :type sell_address: str
        :param buy_address: The address of the token being bought.
        :type buy_address: str
        :param amount: The amount of tokens to be swapped.
        :type amount: int
        :return: The result of the swap.
        :rtype: Any
        :raises ValueError: If the swap fails.
        """
        try:
            uniswap = Uniswap(
                address=self.account.wallet_address,
                private_key=self.account.private_key,
                version=self.protocol_version,
                web3=self.w3,
                factory_contract_addr=settings.dex_factory_contract_addr,
                router_contract_addr=settings.dex_router_contract_addr,
            )
            return uniswap.make_trade(sell_address, buy_address, amount)

        except Exception as error:
            self.logger.debug(error)
            raise ValueError(f"Swap failed {error}")
