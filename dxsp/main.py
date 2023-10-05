"""
 DEX SWAP Main
"""

from typing import Optional

from loguru import logger
from web3 import Web3

from dxsp import __version__
from dxsp.config import settings
from dxsp.protocols import DexKwenta, DexUniswap, DexZeroX


class DexSwap:
    """
    class to build a DexSwap Object
     use to interact with the dex protocol

     Args:
         w3 (Optional[Web3]): Web3

     Returns:
         DexSwap

     Methods:
        _create_client()
        get_quote()
        execute_order()
        get_help()
        get_info()
        get_name()
        get_account_balance()
        get_account_position()



    """

    def __init__(self, w3: Optional[Web3] = None):
        """
        Initialize the DexTrader object
        to interact with exchanges

        """
        try:
            config = settings.dex
            self.clients = []
            for item in config:
                _config = config[item]
                if item in ["", "template"]:
                    continue
                client = self._create_client(
<<<<<<< dev
                    protocol=_config.get("protocol"),
                    name=item,
=======
                    name=item,
                    wallet_address=_config.get("wallet_address"),
                    private_key=_config.get("private_key"),
                    w3=Web3(Web3.HTTPProvider(_config.get("rpc"))),
                    protocol=_config.get("protocol_type"),
                    protocol_version=_config.get("protocol_version"),
                    api_endpoint=_config.get("api_endpoint"),
>>>>>>> origin/dev
                    api_key=_config.get("api_key"),
                    router_contract_addr=_config.get("router_contract_addr"),
                    factory_contract_addr=_config.get("factory_contract_addr"),
                    trading_risk_percentage=_config.get("trading_risk_percentage"),
                    trading_risk_amount=_config.get("trading_risk_amount"),
                    trading_slippage=_config.get("trading_slippage"),
                    trading_asset_address=_config.get("trading_asset_address"),
                    trading_asset_separator=_config.get("trading_asset_separator"),
                    block_explorer_url=_config.get("block_explorer_url"),
                    block_explorer_api=_config.get("block_explorer_api"),
                    mapping=_config.get("mapping"),
                )
                self.clients.append(client)
                logger.debug(f"Loaded {item}")

        except Exception as e:
            logger.error("init: {}", e)

    def _create_client(self, **kwargs):
        protocol = kwargs["protocol"]
        if protocol == "uniswap":
            return DexUniswap(**kwargs)
        elif protocol == "0x":
            return DexZeroX(**kwargs)
        elif protocol == "kwenta":
            return DexKwenta(**kwargs)
        else:
            logger.error(f"protocol type {protocol} not supported")

    async def get_info(self):
        """
        Retrieves information about the exchange
        and the account.

        :return: A formatted string containing
        the exchange name and the account information.
        :rtype: str
        """
        version_info = f"ℹ️ {type(self).__name__} {__version__}\n"
        client_info = "".join(
            f"💱 {client.name}\n🪪 {client.account}\n" for client in self.clients
        )
        return version_info + client_info.strip()

    async def get_quotes(self, sell_token):
        """
        gets a quote for a token

        Args:
            sell_token (str): The sell token.

        Returns:
            str: The quote with the trading symbol

        """
        logger.debug("get quote", sell_token)
        info = "🦄\n"
        for dx in self.clients:
            logger.debug("get quote {}", dx)
            buy_address = dx.trading_asset_address
            sell_token = await dx.replace_instrument(sell_token)
            sell_address = await dx.contract_utils.search_contract_address(sell_token)
            quote = await dx.get_quote(buy_address, sell_address) or "Quote failed"
            symbol = await dx.contract_utils.get_token_symbol(dx.trading_asset_address)
            info += f"{dx.name}: {quote} {symbol}\n"

        return info.strip()

    async def submit_order(self, order_params):
        """
        Execute an order function.

        Args:
            order_params (dict): The order parameters.

        Returns:
            str: The trade confirmation

        """
        try:
            for client in self.clients:
                logger.debug("submit order {}", client)
                action = order_params.get("action")
                instrument = await client.replace_instrument(
                    order_params.get("instrument")
                )
                quantity = order_params.get("quantity", 1)
                sell_token, buy_token = (
                    (client.trading_asset_address, instrument)
                    if action == "BUY"
                    else (instrument, client.trading_asset_address)
                )
                order = await client.get_swap(sell_token, buy_token, quantity)
                if order:
                    trade_confirmation = (
                        f"⬇️ {instrument}"
                        if (action == "SELL")
                        else f"⬆️ {instrument}\n"
                    )
                    trade_confirmation += order
            return trade_confirmation

        except Exception as error:
            return f"⚠️ order execution: {error}"

    # 🔒 USER RELATED
    async def get_balances(self):
        """
        Retrieves the account balance.

        :return: The account balance.
        :rtype: float
        """
        info = "💵\n"
        for client in self.clients:
            info += f"\n{client.name}:"
            info += f"{await client.get_account_balance()}"
        return info.strip()

    async def get_positions(self):
        """
        Retrieves the account position.

        :return: The account position.
        :rtype: AccountPosition
        """
        info = "📊\n"
        for dx in self.clients:
            info += f"\n{dx.name}:"
            info += f"{await dx.get_account_position()}"
        return info.strip()
