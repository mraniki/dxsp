"""
 DEX SWAP Main
"""

import importlib

from loguru import logger

from dxsp import __version__
from dxsp.config import settings


class DexSwap:
    """
    class to build a DexSwap Object
    use to interact with the dex protocol

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

    def __init__(self):
        """
        Initializes the class instance by creating and appending clients
        based on the configuration in `settings.cex`.

        Checks if the module is enabled by looking at `settings.myllm_enabled`.
        If the module is disabled, no clients will be created.

        Creates a mapping of library names to client classes.
        This mapping is used to create new clients based on the configuration.

        If a client's configuration exists in `settings.cex_enabled` and is truthy,
        it will be created.
        Clients are not created if their name is "template" or empty string.

        If a client is successfully created, it is appended to the `clients` list.

        If a client fails to be created, a message is logged with the name of the
        client and the error that occurred.

        Parameters:
            None

        Returns:
            None
        """
        # Check if the module is enabled
        self.enabled = settings.dxsp_enabled or True

        # Create a mapping of library names to client classes
        self.client_classes = self.get_all_client_classes()
        # logger.debug("client_classes available {}", self.client_classes)

        if not self.enabled:
            logger.info("Module is disabled. No clients will be created.")
            return
        self.clients = []
        # Create a client for each client in settings.myllm
        for name, client_config in settings.dex.items():
            # Skip template and empty string client names
            if name in ["", "template"] or not client_config.get("enabled"):
                continue
            try:
                # Create the client
                client = self._create_client(**client_config, name=name)
                # If the client has a valid client attribute, append it to the list
                if client and getattr(client, "client", None):
                    self.clients.append(client)
            except Exception as e:
                # Log the error if the client fails to be created
                logger.error(f"Failed to create client {name}: {e}")

        # Log the number of clients that were created
        logger.info(f"Loaded {len(self.clients)} clients")
        if not self.clients:
            logger.warning(
                """
                No clients were created.
                Check your settings or disable the module.
                https://talky.readthedocs.io/en/latest/02_config.html
                """
            )

    def _create_client(self, **kwargs):
        """
        Create a client based on the given protocol.

        This function takes in a dictionary of keyword arguments, `kwargs`,
        containing the necessary information to create a client. The required
        key in `kwargs` is "library", which specifies the protocol to use for
        communication with the LLM. The value of "library" must match one of the
        libraries supported by MyLLM.

        This function retrieves the class used to create the client based on the
        value of "library" from the mapping of library names to client classes
        stored in `self.client_classes`. If the value of "library" does not
        match any of the libraries supported, the function logs an error message
        and returns None.

        If the class used to create the client is found, the function creates a
        new instance of the class using the keyword arguments in `kwargs` and
        returns it.

        The function returns a client object based on the specified protocol
        or None if the library is not supported.

        Parameters:
            **kwargs (dict): A dictionary of keyword arguments containing the
            necessary information for creating the client. The required key is
            "library".

        Returns:
            A client object based on the specified protocol or None if the
            library is not supported.

        """
        library = kwargs.get("protocol") or kwargs.get("library")
        client_class = self.client_classes.get(f"{library.capitalize()}Handler")

        if client_class is None:
            logger.error(f"library {library} not supported")
            return None

        return client_class(**kwargs)

    def get_all_client_classes(self):
        """
        Retrieves all client classes from the `dxsp.handler` module.

        This function imports the `dxsp.handler` module and retrieves
        all the classes defined in it.

        The function returns a dictionary where the keys are the
        names of the classes and the values are the corresponding
        class objects.

        Returns:
            dict: A dictionary containing all the client classes
            from the `dxsp.handler` module.
        """
        provider_module = importlib.import_module("dxsp.handler")
        return {
            name: cls
            for name, cls in provider_module.__dict__.items()
            if isinstance(cls, type)
        }

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
