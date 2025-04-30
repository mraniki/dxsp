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
        Retrieves a quote for a token swap using 0x API v2.

        Args:
            buy_address (str): The address of the token to be bought.
            buy_symbol (str): The symbol of the token to be bought.
            sell_address (str): The address of the token to be sold.
            sell_symbol (str): The symbol of the token to be sold.
            amount (int, optional): The amount of tokens to be sold. Defaults to 1.

        Returns:
            float: The guaranteed price for the token swap, or None/error message.
        """
        try:
            logger.debug(
                "0x v2 get_quote - buy: {}/{} sell: {}/{} amount: {}",
                buy_address,
                buy_symbol,
                sell_address,
                sell_symbol,
                amount,
            )
            # Resolve buy_token
            buy_token = await self.resolve_token(
                identifier=buy_address
                or buy_symbol
                or self.trading_asset_address
            )

            # Resolve sell_token
            sell_token = await self.resolve_token(
                identifier=sell_address or sell_symbol
            )
            if not buy_token or not sell_token:
                logger.error("Buy or sell token not resolved.")
                return "⚠️ Buy or sell token not found"

            if not self.chain:
                logger.error("Chain ID (self.chain) is not available.")
                return "⚠️ Chain ID not configured"

            amount_wei = amount * (10 ** (sell_token.decimals))
            base_url = "https://api.0x.org/swap/permit2/quote" # V2 endpoint
            params = {
                "chainId": self.chain,
                "buyToken": buy_token.address,
                "sellToken": sell_token.address,
                "sellAmount": str(amount_wei), # API expects string
            }
            # Add taker address if available
            if self.wallet_address:
                params["taker"] = self.wallet_address

            # Construct URL with parameters (requests library handles encoding)
            # We pass params dict to fetch_url instead of embedding in URL string
            logger.debug(f"0x v2 get_quote URL: {base_url} PARAMS: {params}")

            headers = {
                "0x-api-key": self.api_key,
                "0x-version": "v2" # Required V2 header
            }

            # Use fetch_url with params argument
            response = await fetch_url(base_url, params=params, headers=headers)
            logger.debug("0x v2 get_quote response: {}", response)

            if not response:
                return None # fetch_url likely returned None due to e.g., 403

            # Prioritize returning a price if available, even with issues
            price = response.get("guaranteedPrice") or response.get("price")
            if price:
                 # Log issues but still return the price
                if "issues" in response or "validationErrors" in response:
                    logger.warning(f"0x API issues/errors present but price available: {response}")
                return float(price)

            # If no price found, *then* report issues/errors
            if "issues" in response or "validationErrors" in response:
                logger.warning(f"0x API returned issues/errors and no price: {response}")
                reason = response.get("validationErrors", [{}])[0].get("reason", "Validation Error")
                return f"⚠️ 0x Error: {reason}"

            # If none of the above conditions matched
            logger.warning(f"Unknown 0x response structure (no price or known error): {response}")
            return "⚠️ Unknown 0x response"

        except Exception as error:
            logger.exception(f"0x get_quote failed: {error}") # Use logger.exception for stack trace
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
