"""
🔗 EVM

"""
from loguru import logger

# from web3client.base_client import BaseClient
from dxsp.protocols.client import DexClient


class DexEVM(DexClient):
    """
    A DexClient class using coccoinomane web3client
    https://github.com/coccoinomane/web3client

    """

    def __init__(self):
        #super().__init__()
        client = "BaseClient()"
        logger.debug("EVM client {}", client)

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

        Args:
            buy_address (str, optional): The address of the buy token. Defaults to None.
            buy_symbol (str, optional): The symbol of the buy token. Defaults to None.
            sell_address (str, optional):
            The address of the sell token. Defaults to None.
            sell_symbol (str, optional):
            The symbol of the sell token. Defaults to None.
            amount (int, optional): The amount of sell tokens. Defaults to 1.

        Returns:
            Quote
        """
        try:
            logger.debug(
                "evm quote {} {} {} {}",
                buy_address,
                buy_symbol,
                sell_address,
                sell_symbol,
            )  # noqa: E501
            buy_token = await self.resolve_buy_token(
                buy_address=buy_address, buy_symbol=buy_symbol
            )
            sell_token = await self.resolve_sell_token(
                sell_address=sell_address, sell_symbol=sell_symbol
            )
            amount = str(amount * (10**sell_token.decimals))
            logger.debug(f"evm quote {buy_token.address} {sell_token.address} {amount}")

            # return self.client.get_quote()

        except Exception as error:
            logger.error("Quote failed {}", error)

    async def make_swap(self, buy_address, sell_address, amount):
        logger.debug(f"evm make_swap {buy_address} {sell_address} {amount}")
        # swap_order = await self.get_quote(buy_address, sell_address, amount)
        # if swap_order:
        #    return await self.account.get_sign(swap_order)
