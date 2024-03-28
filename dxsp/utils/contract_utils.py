"""
 DEX SWAP
✍️ CONTRACT
"""

from datetime import datetime

import requests
from loguru import logger
from pycoingecko import CoinGeckoAPI

from dxsp.config import settings
from dxsp.utils.utils import fetch_url


class ContractUtils:
    """
    Contract Utils used to interact with the dex protocol

    Args:
        w3 (Optional[Web3]): Web3
        block_explorer_url (Optional[str]): block_explorer_url
        block_explorer_api (Optional[str]): block_explorer_api

    Returns:
        ContractUtils

    Methods:
        get_data()
        search()
        get_cg_platform()
        get_tokenlist_data()
        get_cg_data()
        get_confirmation()

    """

    def __init__(self, w3=None, block_explorer_url=None, block_explorer_api=None):
        """
        Initializes an instance of the class.

        :param w3: An instance of the web3.py library.
        :type w3: web3.Web3

        :param block_explorer_url: The URL of the block explorer.
        :type block_explorer_url: str

        :param block_explorer_api: The API endpoint of the block explorer.
        :type block_explorer_api: str
        """
        self.w3 = w3
        logger.debug("w3: {}", self.w3)
        self.chain = int(self.w3.net.version, 16)
        logger.debug("chain: {}", self.chain)
        self.block_explorer_url = block_explorer_url
        self.block_explorer_api = block_explorer_api
        self.cg = CoinGeckoAPI()
        self.platform = self.get_cg_platform()
        logger.debug("platform: {}", self.platform)

    async def get_data(self, symbol=None, contract_address=None):
        """
        Get data based on the provided symbol or contract address.

        Args:
            symbol (str): The symbol to search for.
            contract_address (str): The contract address of the token.

        Returns:
            Token: The token object containing the data if contract_address is provided.
            None: If neither symbol nor contract_address is provided.
        """
        if symbol:
            return await self.search(symbol)
        if contract_address:
            token = Token(
                w3=self.w3,
                address=contract_address,
            )
            await token.fetch_data()
            return token
        return None

    def get_cg_platform(self):
        """
        Retrieves the platform associated
        with the current network.

        Returns:
            str: The coingecko platform name of the platform associated
            with the current network, or None if no platform is found.

        Raises:
            Exception: If an error occurs
             while retrieving the platform.

        """

        logger.debug("get_cg_platform")
        logger.debug("chain: {}", self.chain)
        network_versions = {
            1: "ethereum",
            10: "optimistic-ethereum",
            56: "binance-smart-chain",
            137: "polygon-pos",
            250: "fantom",
            43114: "avalanche",
            42161: "arbitrum-one",
        }
        if network_name := network_versions.get(self.chain):
            logger.debug("coingecko platform identified {}", network_name)
            return network_name
        try:
            asset_platforms = self.cg.get_asset_platforms()
            output_dict = next(
                x for x in asset_platforms if x["chain_identifier"] == self.chain
            )
            platform = output_dict["id"] or None
            logger.debug("coingecko platform identified {}", platform)
            return platform
        except StopIteration:
            logger.error("No matching platform found for chain: {}", self.chain)
            return None
        except Exception as e:
            logger.error("get_cg_platform: {}", e)
            return None

    async def search(self, token):
        """
        Asynchronously searches for a token based on the given token parameter.

        Args:
            token (str): The token to search for.

        Returns:
            Token: An instance of the Token class representing the found token.

        Raises:
            Exception: If the token is not found.
        """
        try:
            token_instance = await self.search_tokenlist_data(token)
            if token_instance is None:
                logger.info("Searching on Coingecko")
                token_instance = await self.search_cg_data(token)

            if token_instance is None:
                raise Exception(f"Token not found: {token} on {self.chain}")
            token_instance.block_explorer_api = self.block_explorer_api
            token_instance.block_explorer_url = self.block_explorer_url
            return token_instance
        except Exception as e:
            logger.error("Search {}: {}", token, e)
            raise

    async def search_tokenlist_data(self, token):
        """
        Asynchronously searches for tokenlist data based on a given token.

        :param token: The token to search for.
        :type token: str

        :return: An instance of the Token class
        if the tokenlist data is found, else None.
        :rtype: Token or None
        """
        result = await self.get_tokenlist_data(token)
        if result is not None:
            token_instance = Token(w3=self.w3, address=result["address"])
            token_instance.decimals = result["decimals"]
            token_instance.symbol = result["symbol"]
            return token_instance
        return None

    async def get_tokenlist_data(self, symbol):
        """
        Retrieves token data from a given token list URL based on the provided symbol.

        Args:
            symbol (str): The symbol of the token to search for.

        Returns:
            dict or None: The token data if found, None otherwise.
        """
        try:
            token_list_urls = [
                settings.token_personal_list,
                settings.token_testnet_list,
                settings.token_mainnet_list,
            ]

            for token_list_url in token_list_urls:
                if not token_list_url:
                    continue
                logger.debug("Token search in {}", token_list_url)
                token_list = await fetch_url(token_list_url)
                token_search = token_list["tokens"]
                for keyval in token_search:
                    if keyval["symbol"] == symbol and keyval["chainId"] == self.chain:
                        logger.debug("token data found {}", keyval)
                        return keyval
                logger.warning(f"Token {symbol} not found on list")
        except Exception as e:
            logger.error("get_token_data: {}", e)
            return None

    async def search_cg_data(self, token):
        """
        Asynchronously searches for CG data using the provided token.

        :param token: The token to search for.
        :type token: Any

        :return: The token instance if found on Coingecko, otherwise None.
        :rtype: Optional[Token]
        """
        result = await self.get_cg_data(token)
        if result is not None:
            logger.info("Found on Coingecko")
            token_instance = Token(w3=self.w3, address=result["contract_address"])
            token_instance.decimals = result["decimal_place"]
            return token_instance
        return None

    async def get_cg_data(self, token):
        """
        Retrieves data for a given token from the CoinGecko API.

        Args:
            token (str): The symbol of the token to retrieve data for.

        Returns:
            str or None: The data for the token on the specified platform,
                         or None if the token is not found or an error occurs.
        """
        try:
            if self.platform is None:
                return None
            search_results = self.cg.search(query=token)
            search_dict = search_results["coins"]
            filtered_dict = [x for x in search_dict if x["symbol"] == token.upper()]
            api_dict = [sub["api_symbol"] for sub in filtered_dict]
            for i in api_dict:
                coin_dict = self.cg.get_coin_by_id(i)
                try:
                    if coin_dict["detail_platforms"][f"{self.platform}"]:
                        return coin_dict["detail_platforms"][f"{self.platform}"]
                except (KeyError, requests.exceptions.HTTPError):
                    pass
        except Exception as e:
            logger.error("get_cg_data {}", e)

    async def get_confirmation(self, transaction_hash):
        """

        Returns trade confirmation.

        Args:
            transaction_hash (str): The transaction hash

        Returns:
            dict: The trade confirmation

        Raises:
            Exception: Error

        """
        try:
            transaction = self.w3.eth.get_transaction(transaction_hash)
            block_info = self.w3.eth.get_block(transaction["blockNumber"])
            return {
                "timestamp": datetime.utcfromtimestamp(block_info["timestamp"]),
                "id": transaction_hash,
                "instrument": transaction["to"],
                "amount": transaction["value"],
                "price": transaction["gasPrice"],
                "fee": block_info["gasUsed"],
                "confirmation": (
                    f"➕ Size: {round(transaction['value'], 4)}\n"
                    f"ℹ️ {transaction_hash}\n"
                    f"⛽ {block_info['gasUsed']}\n"
                    f"🗓️ {datetime.utcfromtimestamp(block_info['timestamp'])}"
                ),
            }
        except Exception as error:
            logger.error("get_confirmation {}", error)


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

    def __init__(
        self,
        w3=None,
        address=None,
        block_explorer_url=None,
        block_explorer_api=None,
        symbol=None,
    ):
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
            self.w3 = w3
            self.address = self.w3.to_checksum_address(address)
            self.symbol = symbol
            self.block_explorer_url = block_explorer_url
            self.block_explorer_api = block_explorer_api
            self.decimals = None
            self.name = None
            logger.debug("{} - token initialized {}", self.symbol, self.address)
        except Exception as error:
            logger.error("token error {}", error)

    async def fetch_data(self) -> None:
        """
        Retrieves data for the token.
        """
        logger.debug("fetch token data")
        self.contract = await self.get_token_contract()
        self.decimals = await self.get_token_decimals()
        self.symbol = await self.get_token_symbol()
        self.name = await self.get_token_name()
        logger.debug("{} - token data {}", self.symbol, self.address)

    async def get_token_abi(self, address=None):
        """
        Retrieves the ABI (Application Binary Interface)
        of a token contract at the given address.

        Args:
            address (str, optional): The address of the token contract.
            If not provided, the address associated with the
             contract instance is used. Defaults to None.

        Returns:
            str: The ABI of the token contract, if successful.
            None if the request fails or the contract does not have an ABI.
        """
        if not self.block_explorer_api:
            return await fetch_url(settings.dex_erc20_abi_url)
        if address is None:
            address = self.address
        params = {
            "module": "contract",
            "action": "getabi",
            "address": address,
            "apikey": self.block_explorer_api,
        }
        resp = await fetch_url(
            url=self.block_explorer_url, headers=settings.headers, params=params
        )
        if resp:
            return resp["result"] if resp["status"] == "1" else None

    async def get_token_contract(self):
        """
        Retrieves the token contract.

        :return: The token contract.
        """
        self.abi = await self.get_token_abi()
        if self.abi is None:
            return None
        contract = self.w3.eth.contract(address=self.address, abi=self.abi)
        return contract

    def get_contract_function(self, contract, func_name: str):
        """
        Get the contract function by name.

        Args:
            contract: The contract object.
            func_name (str): The name of the function.

        Returns:
            bool: True if the function exists
            in the contract, False otherwise.
        """
        return func_name in dir(contract.functions)

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
        if contract is None or contract.functions is None:
            logger.warning("No Balance")
            return 0
        balance = contract.functions.balanceOf(wallet_address).call()
        if balance is None:
            logger.warning("No Balance")
            return 0
        return round(self.w3.from_wei(balance, "ether"), 5) or 0

    async def get_token_symbol(self):
        """
        Retrieves the symbol of the token.

        Returns:
            str: The symbol of the token.
        """
        contract = await self.get_token_contract()
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
