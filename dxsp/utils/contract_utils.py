"""
 DEX SWAP
✍️ CONTRACT
"""

from datetime import datetime

import requests
from loguru import logger
from pycoingecko import CoinGeckoAPI

from dxsp.utils.token_utils import Token
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

    def __init__(self, **kwargs):
        """
        Initializes an instance of the class.

        :param w3: An instance of the web3.py library.
        :type w3: web3.Web3

        :param block_explorer_url: The URL of the block explorer.
        :type block_explorer_url: str

        :param block_explorer_api: The API endpoint of the block explorer.
        :type block_explorer_api: str
        """
        logger.debug("Initializing ContractUtils")

        # Use local variable to reduce repeated dictionary lookups
        get = kwargs.get

        self.w3 = get("w3", None)
        # Directly convert to int, assuming w3 is always provided
        self.chain = int(self.w3.net.version) if self.w3 else None
        self.abi_url = get("abi_url", None)
        self.token_mainnet_list = get("token_mainnet_list", None)
        self.token_testnet_list = get("token_testnet_list", None)
        self.token_personal_list = get("token_personal_list", None)
        self.headers = get("headers", None)
        self.block_explorer_url = get("block_explorer_url", None)
        self.block_explorer_api = get("block_explorer_api", None)
        self.cg = None
        self.platform = None

        # Logging for debugging purpose
        logger.debug(
            "w3: {}. chain: {}", self.w3, self.chain
        )

    def initialize_platform(self):
        """
        Initialize the platform by making an API call to CoinGecko.
        Call this method when the platform information is actually needed.
        """
        if self.platform is None:
            self.cg = CoinGeckoAPI()
            self.platform = self.get_cg_platform()
            logger.debug("Platform initialized: {}", self.platform)

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
                headers=self.headers,
                abi_url=self.abi_url,
                block_explorer_url=self.block_explorer_url,
                block_explorer_api=self.block_explorer_api,
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

        # logger.debug("get_cg_platform")
        # logger.debug("chain: {}", self.chain)
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
            # logger.debug("coingecko platform identified {}", network_name)
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
                raise Exception(f"Token {token} not found on {self.chain}")
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
            token_instance = Token(
                w3=self.w3,
                address=result["address"],
                headers=self.headers,
                abi_url=self.abi_url,
                block_explorer_api=self.block_explorer_api,
                block_explorer_url=self.block_explorer_url,
            )
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
                self.token_personal_list,
                self.token_testnet_list,
                self.token_mainnet_list,
            ]

            for token_list_url in token_list_urls:
                if not token_list_url:
                    continue
                logger.debug("Token search in {}", token_list_url)
                token_list = await fetch_url(url=token_list_url)
                token_search = token_list["tokens"]
                for keyval in token_search:
                    if keyval["symbol"] == symbol and keyval["chainId"] == self.chain:
                        logger.debug("token data found {}", keyval)
                        return keyval
                    elif keyval["address"] == symbol and keyval["chainId"] == 1:
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
            token_instance = Token(
                w3=self.w3,
                address=result["contract_address"],
                headers=self.headers,
                abi_url=self.abi_url,
                block_explorer_api=self.block_explorer_api,
                block_explorer_url=self.block_explorer_url,
            )
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
        # try:
        self.initialize_platform()
        try:
            if self.platform is None:
                return None
            search_results = self.cg.search(query=token)
            search_dict = search_results["coins"]
            # logger.debug("Coingecko search results: {}", search_dict)
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
