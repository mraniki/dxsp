"""
 DEX SWAP Main
"""

import logging
from typing import Optional

import requests
from pycoingecko import CoinGeckoAPI
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy

from dxsp import __version__
from dxsp.config import settings

class DexSwap:
    """swap  class"""
    def __init__(self, w3: Optional[Web3] = None):
        self.logger = logging.getLogger(name="DexSwap")

        self.w3 = w3 or Web3(Web3.HTTPProvider(settings.dex_rpc))
        self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
        try:
            if self.w3.net.listening:
                self.logger.info("connected %s",self.w3)
        except Exception as error:
            raise error

        self.protocol_type = settings.dex_protocol_type
        self.chain_id = settings.dex_chain_id
        self.wallet_address = self.w3.to_checksum_address(
            settings.dex_wallet_address)
        self.account = str(self.chain_id) + " - "+str(self.wallet_address[-8:])
        self.private_key = settings.dex_private_key

        self.cg = CoinGeckoAPI()

    async def execute_order(self, order_params):
        """Execute swap function."""
        action = order_params.get('action')
        instrument = order_params.get('instrument')
        quantity = order_params.get('quantity', 1)

        try:
            sell_token, buy_token = (
                (settings.trading_asset, instrument)
                if action == 'BUY'
                else (instrument, settings.trading_asset))

            sell_contract = await self.get_token_contract(sell_token)
            sell_decimals = sell_contract.functions.decimals().call() or 18

            sell_balance = await self.get_token_balance(sell_token)
            risk_percentage = settings.trading_risk_amount
            sell_amount = (sell_balance / (risk_percentage ** sell_decimals)) * (float(quantity) / 100)

            order = await self.get_swap(sell_token, buy_token, sell_amount)
            if order:
                return order['confirmation']
        except Exception:
            raise ValueError("Order execution failed")

    async def get_quote(self, sell_token):
        """
        Asynchronously gets a quote for a specified sell token using the given `sell_token` parameter,
        """
        buy_address = await self.search_contract(settings.trading_asset)
        sell_address = await self.search_contract(sell_token)
        if sell_address is None:
            return

        try:
            if self.protocol_type in {"uniswap_v2", "uniswap_v3"}:
                return await self.get_quote_uniswap(
                    buy_address,
                    sell_address)

            if self.protocol_type == "0x":
                return await self.get_0x_quote(
                    buy_address,
                    sell_address)

        except Exception as error:
            raise error

    async def get_swap(self, sell_token: str, buy_token: str, amount: int) -> None:
        """Main swap function"""
        try:
            sell_token_address = await self.search_contract(sell_token)
            sell_token_balance = await self.get_token_balance(sell_token)
            if not sell_token_address or sell_token_balance in (0, None):
                raise ValueError("No Money")

            buy_token_address = await self.search_contract(buy_token)
            if not buy_token_address:
                raise ValueError("contract not found")

            sell_token_amount_wei = self.w3.to_wei(
                amount * 10 ** (await self.get_token_decimals(sell_token)), "ether")

            if await self.get_approve(sell_token) is None:
                raise ValueError("approval failed")

            swap_order = await self.get_swap_order(
                sell_token_address, buy_token_address, sell_token_amount_wei)
            if not swap_order:
                raise ValueError("swawp order not executed")

            if self.protocol_type == "0x":
                await self.get_sign(swap_order)

            signed_order = await self.get_sign(swap_order)
            order_hash = str(self.w3.to_hex(signed_order))

            if self.w3.wait_for_transaction_receipt(
                order_hash, timeout=120, poll_latency=0.1)["status"] != 1:
                return

            await self.get_confirmation(order_hash)

        except Exception as error:
            raise error

### ------🛠️ W3 UTILS ---------


    async def get(self, url, params=None, headers=None):
        try:
            self.logger.debug(f"Requesting URL: {url}")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()

        except Exception as error:
            raise error


    async def router(self):
        try:
            router_abi = await self.get_abi(settings.dex_router_contract_addr)
            if router_abi is None:
                router_abi = await self.get(settings.dex_router_abi_url)
            router = self.w3.eth.contract(
                address=self.w3.to_checksum_address(
                    settings.dex_router_contract_addr),
                abi=router_abi)
            return router
        except Exception as error:
            raise error

    async def get_name(self):
        try:
            return settings.dex_router_contract_addr[-8:]
        except Exception as error:
            raise error

    async def quoter(self):
        try:
            quoter_abi = await self.get_abi(settings.dex_quoter_contract_addr)
            if quoter_abi is None:
                quoter_abi = await self.get(settings.dex_quoter_abi_url)
            contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(
                    settings.dex_quoter_contract_addr),
                abi=quoter_abi)
            return contract
        except Exception as error:
            raise error

    async def get_approve(self, symbol):
        try:
            if self.protocol_type in ["uniswap_v2", "uniswap_v3"]:
                await self.get_approve_uniswap(symbol)
        except Exception as error:
            self.logger.debug("error %s", error)
            return None

    async def get_sign(self, transaction):
        try:
            if self.protocol_type in ['uniswap_v2', 'uniswap_v3']:
                transaction_params = {
                    'from': self.wallet_address,
                    'gas': await self.get_gas(transaction),
                    'gasPrice': await self.get_gas_price(),
                    'nonce': self.w3.eth.get_transaction_count(
                        self.wallet_address),
                }
                transaction = transaction.build_transaction(transaction_params)
            signed = self.w3.eth.account.sign_transaction(
                transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            return tx_hash
        except Exception as error:
            raise error

    async def get_abi(self, address):
        if not settings.dex_block_explorer_api:
            self.logger.warning("No block_explorer_api.")
            return None

        params = {
            "module": "contract",
            "action": "getabi",
            "address": address,
            "apikey": settings.dex_block_explorer_api
        }

        try:
            resp = await self.get(
                url=settings.dex_block_explorer_url, params=params)
            if resp['status'] == "1":
                self.logger.debug("ABI found %s", resp)
                return resp["result"]
            else:
                self.logger.warning("No ABI identified")
                return None
        except Exception as error:
            self.logger.error("get_abi %s", error)
            return None

    async def get_swap_order(self, sell_token_address: str, buy_token_address: str, sell_token_amount_wei: int) -> Optional[str]:
        """Get swap order"""
        order_amount = int(sell_token_amount_wei * (settings.dex_trading_slippage / 100))

        if self.protocol_type in ["uniswap_v2", "uniswap_v3"]:
            return await self.get_swap_uniswap(sell_token_address, buy_token_address, order_amount)
        elif self.protocol_type == "0x":
            order = await self.get_0x_quote(sell_token_address, buy_token_address, order_amount)
            return order if not order else await self.get_sign(order)

        return None

    async def get_confirmation(self, order_hash):
        """Returns trade confirmation."""
        try:
            receipt = self.w3.eth.get_transaction(order_hash)
            block = self.w3.eth.get_block(receipt["blockNumber"])
            trade = {
                "timestamp": block["timestamp"],
                "id": receipt["blockHash"],
                "instrument": receipt["to"],
                "contract": receipt["to"],
                "amount": receipt["value"],
                "price": receipt["value"],  # To be determined.
                "fee": receipt["gas"],
                "confirmation": (
                    f"➕ Size: {round(receipt['value'], 4)}\n"
                    f"⚫️ Entry: {round(receipt['value'], 4)}\n"
                    f"ℹ️ {receipt['blockHash']}\n"
                    f"🗓️ {block['timestamp']}"
                ),
            }
            return trade
        except Exception as error:
            raise error


    async def get_gas(self, transaction):
        """get gas estimate"""
        gas_limit = self.w3.eth.estimate_gas(transaction) * 1.25
        return int(self.w3.to_wei(gas_limit, 'wei'))


    async def get_gas_price(self):
        """search get gas price"""
        gas_price = round(self.w3.from_wei(
            self.w3.eth.generate_gas_price(),
            'gwei'), 2)
        return gas_price

### ------✍️ CONTRACT ---------
    async def search_contract(self, token):
        """search a contract function"""
        self.logger.debug("search_contract")

        try:
            contract_lists = [
                settings.token_personal_list,
                settings.token_testnet_list,
                settings.token_mainnet_list,
            ]

            for contract_list in contract_lists:
                token_contract = await self.get_contract_address(
                    contract_list,
                    token
                )
                if token_contract is not None:
                    self.logger.info("%s token: contract found %s",
                                     token, token_contract)
                    return self.w3.to_checksum_address(token_contract)

            token_contract = await self.search_cg_contract(token)
            if token_contract is not None:
                self.logger.info("%s token: contract found %s",
                                 token, token_contract)
                return self.w3.to_checksum_address(token_contract)

            return None
        except Exception:
            return None

    async def search_cg_platform(self):
        """search coingecko platform"""
        asset_platforms = self.cg.get_asset_platforms()
        output_dict = next(
            x for x in asset_platforms
            if x["chain_identifier"] == int(self.chain_id)
        )
        cg_platform = output_dict["id"] or None
        return cg_platform

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

    async def get_contract_address(self, token_list_url, symbol):
        """Given a token symbol and json tokenlist, get token address"""
        try:
            token_list = await self.get(token_list_url)
            token_search = token_list['tokens']
            for keyval in token_search:
                if (keyval['symbol'] == symbol and
                   keyval['chainId'] == self.chain_id):
                    return keyval['address']
        except Exception as e:
            self.logger.debug("get_contract_address %s", e)
            return

    async def get_token_contract(self, token):
        """Given a token symbol, returns a contract object. """
        try:
            token_address = await self.search_contract(token)
            token_abi = await self.get_abi(token_address)
            if token_abi is None:
                token_abi = await self.get(settings.dex_erc20_abi_url)
            return self.w3.eth.contract(
                address=token_address,
                abi=token_abi)
        except Exception as e:
            raise e

# 🔒 USER RELATED
    async def get_token_balance(self, token_symbol: str) -> Optional[int]:
        """Get token balance"""
        # contract_address = await self.search_contract(token_symbol)
        # if not contract_address:
        #     return None
        contract = await self.get_token_contract(token_symbol)
        if not contract:
            return 0
        return contract.functions.balanceOf(self.wallet_address).call()

    async def get_token_decimals(self, token_symbol: str) -> Optional[int]:
        """Get token decimals"""
        contract = await self.get_token_contract(token_symbol)
        if not contract:
            return 18
        token_decimals = contract.functions.decimals().call() or 18
        return token_decimals

    async def get_account_balance(self):
        try:
            account_balance = self.w3.eth.get_balance(
                self.w3.to_checksum_address(self.wallet_address))
            account_balance = self.w3.from_wei(account_balance, 'ether')
            trading_asset_balance = await self.get_trading_asset_balance()
            if trading_asset_balance:
                account_balance += f"💵{trading_asset_balance}"
            return round(account_balance, 5)

        except Exception:
            return 0

    async def get_trading_asset_balance(self):
        try:
            trading_asset_balance = await self.get_token_balance(
                settings.trading_asset)
            return trading_asset_balance if trading_asset_balance else 0
        except Exception:
            return 0

    async def get_account_position(self):
        return 0

    async def get_account_margin(self):
        return 0

# PROTOCOL SPECIFIC
# uniswap  🦄
    async def get_quote_uniswap(
        self,
        asset_in_address,
        asset_out_address,
        amount=1
    ):
        self.logger.debug("get_quote_uniswap")
        try:
            if self.protocol_type == "uniswap_v2":
                router_instance = await self.router()
                quote = router_instance.functions.getAmountsOut(
                    amount,
                    [asset_in_address, asset_out_address]).call()
                self.logger.error("quote %s", quote)
                if isinstance(quote, list):
                    quote = str(quote[0])
            elif self.protocol_type == "uniswap_v3":
                quoter = await self.quoter()
                sqrtPriceLimitX96 = 0
                fee = 3000
                quote = quoter.functions.quoteExactInputSingle(
                    asset_in_address,
                    asset_out_address,
                    fee, amount, sqrtPriceLimitX96).call()
            return ("🦄 " + quote + " " +
                    settings.trading_asset)
        except Exception as e:
            raise e

    async def get_approve_uniswap(self, symbol):
        try:
            contract = await self.get_token_contract(symbol)
            approved_amount = self.w3.to_wei(2 ** 64 - 1, 'ether')
            owner_address = self.w3.to_checksum_address(self.wallet_address)
            dex_router_address = self.w3.to_checksum_address(settings.dex_router_contract_addr)
            allowance = contract.functions.allowance(owner_address, dex_router_address).call()
            self.logger.debug("allowance %s", allowance)
            if allowance == 0:
                approval_tx = contract.functions.approve(dex_router_address, approved_amount)
                approval_tx_hash = await self.get_sign(approval_tx)
                approval_receipt = self.w3.eth.wait_for_transaction_receipt(
                    approval_tx_hash, timeout=120, poll_latency=0.1)
                return approval_receipt
        except Exception as e:
            raise e


    async def get_swap_uniswap(self, asset_out_address, asset_in_address, amount):
        try:
            path = [self.w3.to_checksum_address(asset_out_address),
                    self.w3.to_checksum_address(asset_in_address)]
            deadline = self.w3.eth.get_block("latest")["timestamp"] + 3600
            router_instance = await self.router()
            min_amount = self.get_quote_uniswap(
                asset_in_address, asset_out_address, amount)[0]

            if self.protocol_type == "uniswap_v2":
                swap_order = router_instance.functions.swapExactTokensForTokens(
                    int(amount), int(min_amount), tuple(path),
                    self.wallet_address, deadline)
                return swap_order
            elif self.protocol_type == "uniswap_v3":
                return None
        except Exception as e:
            raise e

# 0️⃣x
    async def get_0x_quote(self, buy_address, sell_address, amount=1):
        try:
            out_amount = self.w3.to_wei(amount, 'ether')
            url = (settings.dex_0x_url + "/swap/v1/quote?buyToken=" + str(buy_address) +
                "&sellToken=" + str(sell_address) + "&buyAmount=" + str(out_amount))
            headers = {"0x-api-key": settings.dex_0x_api_key}
            response = await self.get(url, params=None, headers=headers)
            print(response)
            if response:
                return round(float(response['guaranteedPrice']), 3)
        except Exception as e:
            raise e
