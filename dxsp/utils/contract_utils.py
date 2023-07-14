"""
 DEX SWAP
✍️ CONTRACT
"""
import logging
from typing import Optional
from web3 import Web3
import requests
from dxsp.config import settings
from dxsp.utils.utils import get, calculate_sell_amount, get_confirmation, get_gas, get_gas_price, get_block_timestamp
from pycoingecko import CoinGeckoAPI

class ContractUtils:

    def __init__(self, w3: Optional[Web3] = None):
        self.logger = logging.getLogger(name="DexSwap")
        self.w3 = w3 or Web3(Web3.HTTPProvider(settings.dex_rpc))
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
            if x["chain_identifier"] == int(self.chain_id)
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
            self.logger.error("search_cg %s", e)
            return

    async def search_cg_contract(self, token):
        """search coingecko contract"""
        try:
            coin_info = await self.search_cg(token)
            return (coin_info['platforms'][f'{await self.search_cg_platform()}']
                    if coin_info is not None else None)
        except Exception as e:
            self.logger.error(" search_cg_contract: %s", e)
            return

    async def get_token_address(self, token_list_url, symbol):
        """Given a token symbol and json tokenlist, get token address"""
        token_list = await get(token_list_url)
        token_search = token_list['tokens']
        for keyval in token_search:
            if (keyval['symbol'] == symbol and
                keyval['chainId'] == self.chain_id):
                return keyval['address']

    async def get_token_contract(self, token_address):
        """Given a token address, returns a contract object. """
        token_abi = await self.get_explorer_abi(token_address)
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


    async def get_token_balance(self, token_address: str) -> Optional[int]:
        """Get token balance"""
        contract = await self.get_token_contract(token_address)
        if contract is None or contract.functions is None:
            raise ValueError("No Balance")
        balance = contract.functions.balanceOf(self.wallet_address).call()
        if balance is None:
            raise ValueError("No Balance")
        return round(self.w3.from_wei(balance, 'ether'),5) or 0

    async def get_explorer_abi(self, address):
        if not settings.dex_block_explorer_api:
            return None

        params = {
            "module": "contract",
            "action": "getabi",
            "address": address,
            "apikey": settings.dex_block_explorer_api
        }
        resp = await get(
            url=settings.dex_block_explorer_url, params=params)
        if resp['status'] == "1":
            self.logger.debug("ABI found %s", resp)
            return resp["result"]
        else:
            return None