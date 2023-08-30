"""
 DEX SWAP
✍️ CONTRACT
"""

import decimal
from datetime import datetime
from typing import Optional

import requests
from loguru import logger
from pycoingecko import CoinGeckoAPI
from web3 import Web3

from dxsp.config import settings
from dxsp.utils.explorer_utils import get_explorer_abi
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
        search_contract_address(self, token)
        search_cg_platform(self)
        search_cg(self, token)
        search_cg_contract(token)
        get_token_address(self, contract_list, token)
        get_token_contract(self, token)
        get_token_decimals(self, token_address)
        get_token_symbol(self, token_address)
        get_token_name(self, token_address)
        get_token_balance(self, token_address)
        calculate_sell_amount(self,
            sell_token_address, wallet_address, quantity)
        get_confirmation(self, tx_hash)

    """

    def __init__(self, w3: Optional[Web3] = None):
        self.logger = logger
        self.w3 = w3
        self.cg = CoinGeckoAPI()

    async def search_contract_address(self, token):
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
            self.logger.debug("Searching Token Address")
            contract_lists = [
                settings.token_personal_list,
                settings.token_testnet_list,
                settings.token_mainnet_list,
            ]
            for contract_list in contract_lists:
                self.logger.debug("Searching {} on {}", token, contract_list)
                token_address = await self.get_token_address(contract_list, token)
                if token_address is not None:
                    self.logger.debug("Found {} on {}", token_address, contract_list)
                    return self.w3.to_checksum_address(token_address)

            self.logger.debug("Searching on Coingecko")
            token_address = await self.search_cg_contract(token)
            if token_address is None:
                self.logger.warning("Invalid Token {}", token)
                raise ValueError(f"Invalid Token {token}")
            self.logger.debug("Found on Coingecko {}", token_address)
            return self.w3.to_checksum_address(token_address)
        except Exception as e:
            self.logger.error(": {}", e)
            raise ValueError(f"Invalid Token {token}")

    async def search_cg_platform(self):
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
        self.logger.debug("coingecko platform identified {}", platform)
        return platform

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
                    if coin_dict["platforms"][f"{await self.search_cg_platform()}"]:
                        return coin_dict
                except (KeyError, requests.exceptions.HTTPError):
                    pass
        except Exception as e:
            self.logger.error("search_cg {}", e)

    async def search_cg_contract(self, token):
        """
        search for a token address on coingecko

        Args:
            token (str): The token symbol

        Returns:
            str: The token address
        """
        try:
            self.logger.debug("Coingecko Address search for {}", token)
            coin_info = await self.search_cg(token)
            return (
                coin_info["platforms"][f"{await self.search_cg_platform()}"]
                if coin_info is not None
                else None
            )
        except Exception as e:
            self.logger.error(" search_cg_contract: {}", e)

    async def get_token_address(self, token_list_url, symbol):
        """

        Given a token symbol and json tokenlist, get token address

        Args:
            token_list_url (str): The token list url
            symbol (str): The token symbol

        Returns:
            str: The token address

        """
        try:
            self.logger.debug("Token address search in {}", token_list_url)
            token_list = await get(token_list_url)
            token_search = token_list["tokens"]
            for keyval in token_search:
                if keyval["symbol"] == symbol and keyval["chainId"] == int(
                    self.w3.net.version
                ):
                    self.logger.debug("token identified")
                    return keyval["address"]
            raise ValueError(f"Token not found {symbol}")
        except Exception as e:
            self.logger.error("get_token_address: {}", e)
            return None

    async def get_token_contract(self, token_address):
        """
        Given a token address, returns a contract object.

        Args:
            token_address (str): The token address

        Returns:
            Contract: The token contract

        """
        token_abi = await get_explorer_abi(token_address)
        if token_abi is None:
            token_abi = await get(settings.dex_erc20_abi_url)
        return self.w3.eth.contract(address=token_address, abi=token_abi)

    async def get_token_decimals(self, token_address: str) -> Optional[int]:
        """
        Get token decimals

        Args:
            token_address (str): The token address

        Returns:
            int: The token decimals

        """
        contract = await self.get_token_contract(token_address)
        return 18 if not contract else contract.functions.decimals().call()

    async def get_token_symbol(self, token_address: str):
        """
        Get token symbol

        Args:
            token_address (str): The token address

        Returns:
            str: The token symbol

        """
        contract = await self.get_token_contract(token_address)
        # token_name = contract.functions.name().call()
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
            raise ValueError("No Balance")
        balance = contract.functions.balanceOf(wallet_address).call()
        if balance is None:
            raise ValueError("No Balance")
        return round(self.w3.from_wei(balance, "ether"), 5) or 0

    async def calculate_sell_amount(self, sell_token_address, wallet_address, quantity):
        """
        Returns amount based on risk percentage.

        Args:
            sell_token_address (str): The sell token address
            wallet_address (str): The wallet address
            quantity (int): The quantity

        Returns:
            float: The sell amount

        """
        sell_balance = await self.get_token_balance(sell_token_address, wallet_address)
        sell_contract = await self.get_token_contract(sell_token_address)
        sell_decimals = (
            sell_contract.functions.decimals().call()
            if sell_contract is not None
            else 18
        )
        risk_percentage = settings.trading_risk_amount
        return (sell_balance / (risk_percentage * 10**sell_decimals)) * (
            decimal.Decimal(quantity) / 100
        )

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
            raise error
