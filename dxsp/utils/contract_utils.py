"""
 DEX SWAP
✍️ CONTRACT
"""

import json
from datetime import datetime
from typing import Optional

import requests
from loguru import logger
from pycoingecko import CoinGeckoAPI

from dxsp.config import settings
from dxsp.utils.utils import get


class ContractUtils:

    """
    ContractUtils class to interact with w3 contracts
    and with coingecko API.
    Coingecko data is retrieve via pycoingecko
    More info: https://github.com/man-c/pycoingecko

    Args:
        w3 (Optional[Web3]): Web3

    Methods:
        search_contract_address()
        search_cg_contract()
        search_cg_platform()
        search_cg_contract()
        get_token_data()
        get_token_symbol()
        get_token_name()
        get_token_decimals()
        get_token_contract()
        get_token_abi()
        get_token_balance()
        calculate_sell_amount()
        get_confirmation()



    """

    def __init__(self, w3=None, block_explorer_url=None, block_explorer_api=None):
        self.w3 = w3
        self.block_explorer_url = block_explorer_url
        self.block_explorer_api = block_explorer_api
        self.cg = CoinGeckoAPI()
        self.platform = self.search_cg_platform() or None

    def search_cg_platform(self):
        """
        Search coingecko platform

        Returns:
            str: The platform

        """
        asset_platforms = self.cg.get_asset_platforms()
        output_dict = next(
            x
            for x in asset_platforms
            if x["chain_identifier"] == int(self.w3.net.version)
        )
        platform = output_dict["id"] or None
        logger.debug("coingecko platform identified {}", platform)
        self.platform = platform
        return platform

    async def search_token_data(self, token):
        """
        Search a contract function on json file
        using tokenlist format https://github.com/Uniswap/token-lists
        or if not in the list verify with coingecko.
        The token list can be modified for your needs.
        The list are defined in settings. Default settings
        are using list under https://github.com/mraniki/tokenlist

        Args:
            token (str): The token address

        Returns:
            str: The token address in w3 checksum format

        Raises:
            ValueError: Invalid Token

        """
        try:
            logger.debug("Searching Token Address")
            contract_lists = [
                settings.token_personal_list,
                settings.token_testnet_list,
                settings.token_mainnet_list,
            ]
            for contract_list in contract_lists:
                if not contract_list:
                    continue
                logger.debug("Searching {} on {}", token, contract_list)
                token_data = await self.get_token_data(contract_list, token)
                if token_data is not None:
                    logger.debug("Found {} on {}", token_data, contract_list)
                    return token_data

            logger.debug("Searching on Coingecko")
            token_data = await self.search_cg_contract(token)
            if token_data is None:
                logger.warning("Invalid Token {}", token)
            logger.debug("Found on Coingecko {}", token_data)
            return token_data
        except Exception as e:
            logger.error("Invalid Token {}: {}", token, e)

    async def search_cg(self, token):
        """
        Search Coingecko

        Args:
            token (str): The token symbol

        Returns:
            str: The token dictionary for the platform


        """
        try:
            search_results = self.cg.search(query=token)
            search_dict = search_results["coins"]
            filtered_dict = [x for x in search_dict if x["symbol"] == token.upper()]
            api_dict = [sub["api_symbol"] for sub in filtered_dict]
            for i in api_dict:
                coin_dict = self.cg.get_coin_by_id(i)
                try:
                    if coin_dict["platforms"][f"{self.platform()}"]:
                        return coin_dict
                except (KeyError, requests.exceptions.HTTPError):
                    pass
        except Exception as e:
            logger.error("search_cg {}", e)

    async def search_cg_contract(self, token):
        """
        search for a token address on coingecko

        Args:
            token (str): The token symbol

        Returns:
            str: The token address
        """
        try:
            logger.debug("Coingecko Address search for {}", token)
            coin_info = await self.search_cg(token)
            logger.debug("coin_info {}", coin_info)
            return (
                coin_info["platforms"][f"{self.platform}"]
                if coin_info is not None
                else None
            )
        except Exception as e:
            logger.error(" search_cg_contract: {}", e)

    async def search_cg_token_data(self, token_address):
        """
        search token data on coingecko
        """
        return self.cg.get_coin_info_from_contract_address_by_id(
            id=self.platform, contract_address=token_address
        )

    async def get_token_data(self, token_list_url, symbol):
        """

        Given a token symbol and json tokenlist, get token address

        Args:
            token_list_url (str): The token list url
            symbol (str): The token symbol

        Returns:
            str: The token address

        """
        try:
            logger.debug("Token address search in {}", token_list_url)
            token_list = await get(token_list_url)
            token_search = token_list["tokens"]
            for keyval in token_search:
                if keyval["symbol"] == symbol and keyval["chainId"] == int(
                    self.w3.net.version
                ):
                    logger.debug("token identified")
                    return keyval
            logger.warning(f"Token not found {symbol}")
        except Exception as e:
            logger.error("get_token_data: {}", e)
            return None

    async def get_token_symbol(self, token_address: str):
        """
        Get token symbol

        Args:
            token_address (str): The token address

        Returns:
            str: The token symbol

        """
        contract = await self.get_token_contract(token_address)
        return contract.functions.symbol().call()

    async def get_token_name(self, token_address: str):
        """
        Get token symbol

        Args:
            token_address (str): The token address

        Returns:
            str: The token name

        """
        contract = await self.get_token_contract(token_address)
        return contract.functions.name().call()

    async def get_token_decimals(self, token_address: str) -> Optional[int]:
        """
        Get token decimals

        Args:
            token_address (str): The token address

        Returns:
            int: The token decimals

        
        """
        search = await self.search_token_data(token_address)
        if search:
            return search["decimals"]
        contract = await self.get_token_contract(token_address)
        return 18 if not contract else contract.functions.decimals().call()

    async def get_token_contract(self, token_address):
        """Returns the contract object for a given token address.

        Args:
            token_address (str): The address of the token.

        Returns:
            contract: The contract object for the token.
        """
        # Get the ABI for the token address
        token_abi = await self.get_token_abi(token_address)
        logger.debug("token abi: {}", token_abi)

        # Check if the ABI has an implementation object
        

        # If the ABI is not found, try to get it from a default URL
        if token_abi is None:
            token_abi = await get(settings.dex_erc20_abi_url)

        # If the ABI has an implementation, get the ABI for the implementation
        # elif proxy is not None:
        #     proxy = next(
        #     (
        #         obj
        #         for obj in json.loads(token_abi.text)
        #         if obj["name"] == "implementation"
        #     ),
        #     None,
        #     )
        #     token_abi = await self.get_token_abi(proxy)

        # Return the contract object with the token address and ABI
        return self.w3.eth.contract(address=token_address, abi=token_abi)

    async def get_token_abi(self, address):
        """
        Retrieves the ABI (Application Binary Interface)
        for the contract at the given address.

        :param address: The address of the contract.
        :type address: str

        :return: The ABI of the contract if it exists, else None.
        :rtype: str or None
        """
        if not self.block_explorer_api:
            return None

        params = {
            "module": "contract",
            "action": "getabi",
            "address": address,
            "apikey": self.block_explorer_api,
        }
        resp = await get(
            url=self.block_explorer_url, headers=settings.headers, params=params
        )
        if resp:
            logger.debug("get_token_abi: {}", resp)
            return resp["result"] if resp["status"] == "1" else None

    async def get_token_balance(
        self, token_address: str, wallet_address: str
    ) -> Optional[int]:
        """
        Get token balance

        Args:
            token_address (str): The token address
            wallet_address (str): The wallet address

        Returns:
            int: The token balance

        """
        contract = await self.get_token_contract(token_address)
        if contract is None or contract.functions is None:
            logger.warning("No Balance")
            return 0
        balance = contract.functions.balanceOf(wallet_address).call()
        if balance is None:
            logger.warning("No Balance")
            return 0
        return round(self.w3.from_wei(balance, "ether"), 5) or 0

    async def get_confirmation(self, transactionHash):
        """

        Returns trade confirmation.

        Args:
            transactionHash (str): The transaction hash

        Returns:
            dict: The trade confirmation

        Raises:
            Exception: Error

        """
        try:
            transaction = self.w3.eth.get_transaction(transactionHash)
            block_info = self.w3.eth.get_block(transaction["blockNumber"])
            return {
                "timestamp": datetime.utcfromtimestamp(block_info["timestamp"]),
                "id": transactionHash,
                "instrument": transaction["to"],
                "contract": transaction["to"],  # TBD To be determined.
                "amount": transaction["value"],
                "price": transaction["value"],  # TBD To be determined.
                "fee": transaction["gas"],
                "confirmation": (
                    f"➕ Size: {round(transaction['value'], 4)}\n"
                    f"⚫️ Entry: {round(transaction['value'], 4)}\n"
                    f"ℹ️ {transactionHash}\n"
                    f"⛽ {transaction['gas']}\n"
                    f"🗓️ {datetime.utcfromtimestamp(block_info['timestamp'])}"
                ),
            }
        except Exception as error:
            logger.error("get_confirmation {}", error)
