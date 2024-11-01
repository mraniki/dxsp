# """
# OneInch 🦄
# """

# from ._client import DexClient


# class OneinchHandler(DexClient):
#     """
#     DexClient using 1inch protocol
#     https://github.com/mraniki/dxsp/issues/189

#     """
# def __init__(
#     self,
#     **kwargs,
# ):
#     """
#     Initialize the client

#     """
#     super().__init__(**kwargs)
#     self.client = "1inch"

#     async def get_quote(self, buy_address=None, symbol=None, amount=1):
#         """
#         Retrieves a quote for the
#         given buy and sell addresses and amount.

#         Args:
#             buy_address (str): The address of the token to buy.
#             sell_address (str): The address of the token to sell.
#             amount (int, optional): The amount of tokens to buy. Defaults to 1.

#         Returns:
#             float: The quote amount rounded to 2 decimal places.
#         """
#         pass
#         # try:
#         #     min_amount = self.w3.to_wei(amount, "ether")
#         #     quote_url = (
#         #         settings.dex_1inch_url
#         #         + str(self.chain_id)
#         #         + "/quote?fromTokenAddress="
#         #         + str(buy_address)
#         #         + "&toTokenAddress="
#         #         + str(sell_address)
#         #         + "&amount="
#         #         + str(min_amount)
#         #     )
#         #     quote_response = await self._get(
#         #         url=quote_url, params=None, headers=settings.headers
#         #     )
#         #     logger.debug("quote_response {}", quote_response)
#         #     if quote_response:
#         #         quote_amount = quote_response["toTokenAmount"]
#         #         logger.debug("quote_amount {}", quote_amount)
#         #         quote_decimals = quote_response["fromToken"]["decimals"]
#         #         return round(
#         #             self.w3.from_wei(int(quote_amount), "ether")
#         #             / (10**quote_decimals),
#         #             2,
#         #         )
#         # except Exception as error:
#         #     raise ValueError(f"Approval failed {error}")

#     # async def get_approve(self, token_address):
#     #     # pass
#     #     try:
#     #         pass
#     # approval_check_URL = (
#     #     settings.dex_1inch_url
#     #     + str(self.chain_id)
#     #     + "/approve/allowance?tokenAddress="
#     #     + str(sell_address)
#     #     + "&walletAddress="
#     #     + str(self.wallet_address))
#     # approval_response = await self._get(
#     #     url=approval_check_URL,
#     #     params=None,
#     #     headers=settings.headers)
#     # approval_check = approval_response['allowance']
#     # if (approval_check == 0):
#     #     approval_URL = (
#     #         settings.dex_1inch_url
#     #         + str(self.chain_id)
#     #         + "/approve/transaction?tokenAddress="
#     #         + str(sell_address))
#     #     approval_response = await self._get(approval_URL)
#     #     return approval_response
#     #     except Exception as error:
#     #         raise ValueError(f"Approval failed {error}")

#     # async def make_swap(self, sell_address, buy_address, amount):

#     #     try:
#     #         pass
#     # swap_url = (
#     #     settings.dex_1inch_url
#     #     + str(self.chain_id)
#     #     + "/swap?fromTokenAddress="
#     #     + sell_address
#     #     + "&toTokenAddress="
#     #     + buy_address
#     #     + "&amount="
#     #     + amount
#     #     + "&fromAddress="
#     #     + self.wallet_address
#     #     + "&slippage="
#     #     + settings.dex_trading_slippage
#     #     )
#     # swap_order = await self._get(
#     #     url=swap_url,
#     #     params=None,
#     #     headers=settings.headers
#     #     )
#     # swap_order_status = swap_order['statusCode']
#     # if swap_order_status != 200:
#     #     return
#     # return swap_order
#     # except Exception as error:
#     #     raise ValueError(f"Swap failed {error}")
