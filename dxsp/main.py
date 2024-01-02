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
        get_info
        get_balances
        get_positions
        get_pnl
        get_quotes()
        submit_order

    """

    def __init__(self, w3: Optional[Web3] = None):
        """
        Initialize the DexTrader object
        to interact with exchanges

        """
        try:
            logger.info("Initializing DexSwap")
            config = settings.dex
            self.clients = []
            for item in config:
                logger.debug("Client configuration starting: {}", item)
                _config = config[item]
                if item in ["", "template"]:
                    continue
                protocol = _config.get("protocol") or "uniswap"
                if protocol not in ["uniswap", "0x", "kwenta"]:
                    logger.warning(
                        f"Skipping client creation for unsupported protocol: {protocol}"
                    )
                    continue
                logger.debug("Client protocol: {}", protocol)
                client = self._create_client(
                    name=item,
                    wallet_address=_config.get("wallet_address"),
                    private_key=_config.get("private_key"),
                    rpc=_config.get("rpc"),
                    w3=Web3(Web3.HTTPProvider(_config.get("rpc"))),
                    protocol=protocol,
                    protocol_version=_config.get("protocol_version") or 2,
                    api_endpoint=_config.get("api_endpoint") or "https://api.0x.org/",
                    api_key=_config.get("api_key") or None,
                    router_contract_addr=_config.get("router_contract_addr") or None,
                    factory_contract_addr=_config.get("factory_contract_addr") or None,
                    trading_risk_percentage=_config.get("trading_risk_percentage")
                    or True,
                    trading_risk_amount=_config.get("trading_risk_amount") or 1,
                    trading_slippage=_config.get("trading_slippage") or 2,
                    trading_asset_address=_config.get("trading_asset_address"),
                    trading_asset_separator=_config.get("trading_asset_separator")
                    or "",
                    block_explorer_url=_config.get("block_explorer_url") or None,
                    block_explorer_api=_config.get("block_explorer_api") or None,
                    mapping=_config.get("mapping") or None,
                )

                self.clients.append(client)
                logger.debug(f"Loaded {item}")
            if self.clients:
                logger.info(f"Loaded {len(self.clients)} DEX clients")
            else:
                logger.warning("No DEX clients loaded. Verify config")

        except Exception as e:
            logger.error("init: {}", e)

    def _create_client(self, **kwargs):
        """

        Create a client based on the given protocol.

        Parameters:
            **kwargs (dict): Keyword arguments that
            contain the necessary information for creating the client.
            The "protocol" key is required.

        Returns:
            client object based on
            the specified protocol.

        """
        logger.debug("Creating client {}", kwargs["protocol"])
        if kwargs["protocol"] == "0x":
            return DexZeroX(**kwargs)
        elif kwargs["protocol"] == "kwenta":
            return DexKwenta(**kwargs)
        else:
            return DexUniswap(**kwargs)

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
            f"💱 {client.name} {client.account_number}\n" for client in self.clients
        )
        return version_info + client_info.strip()

    async def get_balances(self):
        """
        Retrieves the account balance.

        :return: The account balance.
        :rtype: float
        """
        _info = ["🏦 Balance"]
        for client in self.clients:
            _info.append(f"\n{await client.get_account_balance()}")
        return "\n".join(_info)

    async def get_positions(self):
        """
        Retrieves the account position.

        :return: The account position.
        :rtype: AccountPosition
        """
        _info = ["📊\n"]
        for client in self.clients:
            _info.append(f"{client.name}:\n{await client.get_account_position()}")
        return "\n".join(_info)

    async def get_pnl(self):
        """
        Retrieves the account position.

        :return: The account position.
        :rtype: AccountPosition
        """
        _info = ["🏆\n"]
        for client in self.clients:
            _info.append(f"{client.name}:\n{await client.get_account_pnl()}")
        return "\n".join(_info)

    async def get_quotes(self, symbol=None, address=None):
        """
        gets a quote for a token

        Args:
            sell_token (str): The sell token.

        Returns:
            str: The quote with the trading symbol

        """
        _info = ["⚖️\n"]
        for client in self.clients:
            try:
                quote = await client.get_quote(sell_symbol=symbol, sell_address=address)
                client_info = f"{client.name}: {quote}"
                _info.append(client_info)
                logger.debug("Retrieved quote for {}: {}", client.name, quote)
            except Exception as error:
                logger.error("Error retrieving quote for {}: {}", client.name, error)

        # Aggregated quote information logged at once
        logger.debug("All quotes: {}", " | ".join(_info))
        return "\n".join(_info)

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
                        f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
                    )
                    trade_confirmation += order
            return trade_confirmation

        except Exception as error:
            return f"⚠️ order execution: {error}"
