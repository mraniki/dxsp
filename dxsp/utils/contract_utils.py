"""
 DEX SWAP
✍️ CONTRACT
"""

import decimal
import logging
from datetime import datetime
from typing import Optional

import requests
from pycoingecko import CoinGeckoAPI
from web3 import Web3

from dxsp.config import settings
from dxsp.utils.explorer_utils import get_explorer_abi
from dxsp.utils.utils import get


class ContractUtils:

    def __init__(self, w3: Optional[Web3] = None):
        self.logger = logging.getLogger(name="DexSwap")
        self.w3 = w3
        self.cg = CoinGeckoAPI()

    async def search_contract_address(self, token):
        """search a contract function"""

        contract_lists = [
            settings.token_personal_list,
            settings.token_testnet_list,
            settings.token_mainnet_list,
        ]
        for contract_list in contract_lists:
            token_address = await self.get_token_address(
                contract_list,
                token
            )
            if token_address is not None:
                return self.w3.to_checksum_address(token_address)

        token_address = await self.search_cg_contract(token)
        if token_address is None:
            if settings.dex_notify_invalid_token:
                raise ValueError("Invalid Token")
            return
        return self.w3.to_checksum_address(token_address)

    async def search_cg_platform(self):
        """search coingecko platform"""
        asset_platforms = self.cg.get_asset_platforms()
        output_dict = next(
            x for x in asset_platforms
            if x["chain_identifier"] == int(self.w3.net.version)
        )
        return output_dict["id"] or None

    async def search_cg(self, token):
        """search coingecko"""
        try:
            search_results = self.cg.search(query=token)
            search_dict = search_results['coins']
            filtered_dict = [x for x in search_dict if
                             x['symbol'] == token.upper()]
            api_dict = [sub['api_symbol'] for sub in filtered_dict]
            for i in api_dict:
                coin_dict = self.cg.get_coin_by_id(i)
                try:
                    if coin_dict['platforms'][f'{await self.search_cg_platform()}']:
                        return coin_dict
                except (KeyError, requests.exceptions.HTTPError):
                    pass
        except Exception as e:
            self.logger.error("search_cg {}", e)
            return

    async def search_cg_contract(self, token):
        """search coingecko contract"""
        try:
            coin_info = await self.search_cg(token)
            return (coin_info['platforms'][f'{await self.search_cg_platform()}']
                    if coin_info is not None else None)
        except Exception as e:
            self.logger.error(" search_cg_contract: {}", e)
            return

    async def get_token_address(self, token_list_url, symbol):
        """Given a token symbol and json tokenlist, get token address"""
        token_list = await get(token_list_url)
        token_search = token_list['tokens']
        for keyval in token_search:
            if (keyval['symbol'] == symbol and
                keyval['chainId'] == int(self.w3.net.version)):
                return keyval['address']
 
    async def get_token_contract(self, token_address):
        """Given a token address, returns a contract object. """
        token_abi = await get_explorer_abi(token_address)
        if token_abi is None:
            token_abi = await get(settings.dex_erc20_abi_url)
        return self.w3.eth.contract(
            address=token_address,
            abi=token_abi)

    async def get_token_decimals(self, token_address: str) -> Optional[int]:
        """Get token decimals"""
        contract = await self.get_token_contract(token_address)
        return 18 if not contract else contract.functions.decimals().call()

    async def get_token_symbol(self, token_address: str):
        """Get token symbol"""
        contract = await self.get_token_contract(token_address)
        #token_name = contract.functions.name().call()
        return contract.functions.symbol().call() 

    async def get_token_name(self, token_address: str):
        """Get token symbol"""
        contract = await self.get_token_contract(token_address)
        return contract.functions.name().call() 

    async def get_token_balance(
        self, token_address: str,
        wallet_address: str
        ) -> Optional[int]:
        """Get token balance"""
        contract = await self.get_token_contract(token_address)
        if contract is None or contract.functions is None:
            raise ValueError("No Balance")
        balance = contract.functions.balanceOf(wallet_address).call()
        if balance is None:
            raise ValueError("No Balance")
        return round(self.w3.from_wei(balance, 'ether'),5) or 0


    async def calculate_sell_amount(self, sell_token_address, wallet_address, quantity):
        """Returns amount based on risk percentage."""
        sell_balance = await self.get_token_balance(
            sell_token_address, wallet_address)
        sell_contract = await self.get_token_contract(sell_token_address)
        sell_decimals = (
            sell_contract.functions.decimals().call()
            if sell_contract is not None else 18)
        risk_percentage = settings.trading_risk_amount
        return ((sell_balance / (risk_percentage * 10 ** sell_decimals))
                * (decimal.Decimal(quantity)/ 100)) 


    async def get_confirmation(self, transactionHash):
        """Returns trade confirmation."""
        try:
            transaction = self.w3.eth.get_transaction(transactionHash)
            block_info = self.w3.eth.get_block(transaction["blockNumber"])
            return {
                "timestamp": datetime.utcfromtimestamp(block_info['timestamp']),
                "id": transactionHash,
                "instrument": transaction["to"],
                "contract": transaction["to"],   # TBD To be determined.
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
