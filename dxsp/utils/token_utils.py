"""
 DEX SWAP
🪙 TOKEN
"""

from loguru import logger

from dxsp.utils.utils import fetch_url


class Token:
    """

    Class Token to interact with web3 token contract

    Args:
        w3: An instance of the web3 library.
        address: The address of the token contract.
        block_explorer_url: The URL of the block explorer for the token.
        block_explorer_api: The API endpoint of the block explorer for the token.
        symbol: The symbol of the token.

    Returns:
        Token

    Methods:
        __init__: Initializes an instance of the class.
        fetch_data: Retrieves data for the token.
        get_token_abi: Retrieves the token abi.
        get_token_contract: Retrieves the token contract.
        get_contract_function: Retrieves the contract functions by name.
        get_token_balance: Retrieves the token balance.
        get_token_symbol: Retrieves the token symbol.
        get_token_name: Retrieves the token name.
        get_token_decimals: Retrieves the token decimals.

    """

    def __init__(self, **kwargs):
        """
        Initializes an instance of the class.

        :param w3: An instance of the web3 library.
        :type w3: object

        :param address: The address of the token contract.
        :type address: str

        :param block_explorer_url: The URL of the block explorer for the token.
        :type block_explorer_url: str

        :param block_explorer_api: The API endpoint of the block explorer for the token.
        :type block_explorer_api: str

        :param symbol: The symbol of the token.
        :type symbol: str
        """
        try:
            get = kwargs.get
            logger.debug("initializing token")
            self.w3 = get("w3", None)
            self.address = self.w3.to_checksum_address(get("address", None))
            self.symbol = get("symbol", None)
            self.headers = get("headers", None)
            self.abi_url = get("abi_url", None)
            self.block_explorer_url = get("block_explorer_url", None)
            self.block_explorer_api = get("block_explorer_api", None)
            self.decimals = None
            self.name = None
            logger.debug(
                "token initialized symbol {} address {}", self.symbol, self.address
            )
        except Exception as error:
            logger.error("token error {}", error)

    async def fetch_data(self) -> None:
        """
        Retrieves data for the token.
        """
        logger.debug("fetch token data")
        self.contract = await self.get_token_contract() or None
        self.decimals = await self.get_token_decimals() or 18
        self.symbol = await self.get_token_symbol() or None
        self.name = await self.get_token_name() or None
        logger.debug("{} - token data {}", self.symbol, self.address)

    async def get_token_abi(self, address=None):
        """
        Retrieves the ABI (Application Binary Interface)
        of a token contract at the given address.
        First, it tries to fetch the ABI from the block explorer
        if the block explorer url and api key are provided.
        If not, it tries to fetch the ABI from the dex ERC20 ABI URL

        Args:
            address (str, optional): The address of the token contract.
            If not provided, the address associated with the
             contract instance is used. Defaults to None.

        Returns:
            str: The ABI of the token contract, if successful.
            None if the request fails or the contract does not have an ABI.
        """
        if self.block_explorer_url and self.block_explorer_api:
            if address is None:
                address = self.address
            params = {
                "module": "contract",
                "action": "getabi",
                "address": address,
                "apikey": self.block_explorer_api,
            }
            resp = await fetch_url(
                url=self.block_explorer_url, headers=self.headers, params=params
            )
            if resp:
                return resp["result"] if resp["status"] == "1" else None

        logger.warning("No block explorer url or api key provided")
        return await fetch_url(url=self.abi_url)

    async def get_token_contract(self):
        """
        Retrieves the token contract.

        :return: The token contract.
        """
        self.abi = await self.get_token_abi()
        logger.debug("token abi {}", self.abi)
        if self.abi is None:
            return None
        contract = self.w3.eth.contract(address=self.address, abi=self.abi)
        return contract

    # def get_contract_function(self, contract, func_name: str):
    #     """
    #     Get the contract function by name.

    #     Args:
    #         contract: The contract object.
    #         func_name (str): The name of the function.

    #     Returns:
    #         bool: True if the function exists
    #         in the contract, False otherwise.
    #     """
    #     return func_name in dir(contract.functions)

    async def get_token_balance(self, wallet_address):
        """
        Get the balance of a token for a given wallet address.

        Args:
            wallet_address (str): The wallet
            address to check the balance for.

        Returns:
            float: The balance of the token in ether.

        Raises:
            None
        """
        contract = await self.get_token_contract()
        if not contract or contract.functions is None:
            logger.warning("No Balance")
            return 0
        balance = contract.functions.balanceOf(wallet_address).call()
        return round(self.w3.from_wei(balance, "ether"), 5) or 0

    async def get_token_symbol(self):
        """
        Retrieves the symbol of the token.

        Returns:
            str: The symbol of the token.
        """
        contract = await self.get_token_contract()
        if contract:
            return contract.functions.symbol().call()

    async def get_token_name(self):
        """
        Get the name of the token.

        Args:
            self: The object itself.

        Returns:
            The name of the token as a string.
        """
        contract = await self.get_token_contract()
        if contract:
            return contract.functions.name().call()

    async def get_token_decimals(self):
        """
        Get the number of decimal places for the token.

        Returns:
            int: The number of decimal places for the token.
        """
        if self.decimals is not None:
            return self.decimals
        contract = await self.get_token_contract()
        return contract.functions.decimals().call() if contract else 18
