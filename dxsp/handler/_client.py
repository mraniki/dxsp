"""
Base DexClient Class   🦄
"""

import asyncio
import decimal
from datetime import datetime, timedelta

import aiohttp
from loguru import logger
from web3 import Web3

# from web3.exceptions import Web3Exception
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware
from web3.types import TxData

from dxsp.utils import AccountUtils, ContractUtils, WalletMonitor


class DexClient:
    """
    Base DexClient Class for handler base

    Args:
        **kwargs: Keyword arguments containing the following:
            - name (str): The name of the client.
            - protocol (str): The protocol to use (default: "uniswap").
            - protocol_version (int): The version of the protocol (default: 2).
            - api_endpoint (str): The API endpoint.
            - api_key (str): The API key.
            - rpc (str): The RPC URL.
            - w3 (Web3): The Web3 instance.
            - router_contract_addr (str): The router contract address.
            - factory_contract_addr (str): The factory contract address.
            - trading_asset_address (str): The trading asset address.
            - trading_risk_percentage (float): The trading risk percentage.
            - trading_asset_separator (str): The trading asset separator.
            - trading_risk_amount (float): The trading risk amount.
            - trading_slippage (float): The trading slippage.
            - trading_amount_threshold (float): The trading amount threshold.
            - block_explorer_url (str): The block explorer URL.
            - block_explorer_api (str): The block explorer API.
            - mapping (dict): The mapping.
            - is_pnl_active (bool): Indicates if PnL is active (default: False).
            - rotki_report_endpoint (str): The Rotki report endpoint.
            - follow_wallet (bool): Enable wallet monitoring (default: False).
            - follow_wallet_address (str): Wallet address to monitor.
            - follow_wallet_functions (list[str]): Function names to copy
              (default: ["swapExactTokensForTokens"])

    Returns:
        None

    Methods:
        resolve_buy_token
        resolve_sell_token
        resolve_token
        replace_instrument
        get_order_amount
        get_quote
        get_swap
        make_swap
        get_account_balance
        get_trading_asset_balance
        get_account_position
        get_account_margin
        get_account_open_positions
        get_account_pnl
        calculate_pnl
        _run_monitoring_loop
        _handle_monitored_transaction

    """


    def __init__(self, **kwargs):
        """
        Initializes the DexClient object.

        Args:
            **kwargs: Keyword arguments containing the following:
                - name (str): The name of the client.
                - protocol (str): The protocol to use (default: "uniswap").
                - protocol_version (int): The version of the protocol (default: 2).
                - api_endpoint (str): The API endpoint.
                - api_key (str): The API key.
                - rpc (str): The RPC URL.
                - w3 (Web3): The Web3 instance.
                - router_contract_addr (str): The router contract address.
                - factory_contract_addr (str): The factory contract address.
                - trading_asset_address (str): The trading asset address.
                - trading_risk_percentage (float): The trading risk percentage.
                - trading_asset_separator (str): The trading asset separator.
                - trading_risk_amount (float): The trading risk amount.
                - trading_slippage (float): The trading slippage.
                - trading_amount_threshold (float): The trading amount threshold.
                - block_explorer_url (str): The block explorer URL.
                - block_explorer_api (str): The block explorer API.
                - mapping (dict): The mapping.
                - is_pnl_active (bool): Indicates if PnL is active (default: False).
                - rotki_report_endpoint (str): The Rotki report endpoint.
                - follow_wallet (bool): Enable wallet monitoring (default: False).
                - follow_wallet_address (str): Wallet address to monitor.
                - follow_wallet_functions (list[str]): Function names to copy
                  (default: ["swapExactTokensForTokens"])

        Returns:
            None
        """
        get = kwargs.get
        self.name = get("name", None)
        logger.debug(f"Setting up: {self.name}")

        self.protocol = get("library") or get("protocol") or "uniswap"
        self.protocol_version = get("library_version") or get("protocol_version") or 2
        self.api_endpoint = get("api_endpoint", None)
        self.api_key = get("api_key", None)
        self.rpc = get("rpc", None)
        self.w3 = get("w3", None)
        self.wallet_address = get("wallet_address", None)
        self.private_key = get("private_key", None)
        self.headers = get("headers", "{User-Agent= 'Mozilla/5.0'}")
        self.abi_url = get(
            "abi_url",
            "https://raw.githubusercontent.com/Uniswap/interface/44c355c7f0f8ab5bdb3e0790560e84e59f5666f7/src/abis/erc20.json",
        )
        self.token_mainnet_list = get("token_mainnet_list", None)
        self.token_testnet_list = get("token_testnet_list", None)
        self.token_personal_list = get("token_personal_list", None)
        self.router_contract_addr = get("router_contract_addr", None)
        self.factory_contract_addr = get("factory_contract_addr", None)
        self.trading_asset_address = get("trading_asset_address", None)
        self.trading_risk_percentage = get("trading_risk_percentage", None)
        self.trading_asset_separator = get("trading_asset_separator", None)
        self.trading_risk_amount = get("trading_risk_amount", None)
        self.trading_slippage = get("trading_slippage", None)
        self.trading_amount_threshold = get("trading_amount_threshold", None)
        self.block_explorer_url = get("block_explorer_url", None)
        self.block_explorer_api = get("block_explorer_api", None)
        self.mapping = get("mapping", None)
        self.is_pnl_active = get("is_pnl_active", False)
        self.rotki_report_endpoint = get("rotki_report_endpoint", None)
        self.follow_wallet = get("follow_wallet", False)
        self.follow_wallet_address = get("follow_wallet_address", None)
        self.follow_wallet_functions = get(
            "follow_wallet_functions", ["swapExactTokensForTokens"]
        )

        self.client = None
        self.chain = None
        self.account_number = None
        self.wallet_monitor = None
        self._monitor_task = None

        if self.rpc:
            try:
                self.w3 = Web3(Web3.HTTPProvider(self.rpc))
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
                logger.debug(
                    f"Chain {self.w3.net.version} - {int(self.w3.net.version, 16)}"
                )
            except Exception as e:
                logger.error(f"Invalid RPC URL or response: {e}")
                self.w3 = None

        if self.w3 and self.wallet_address:
            self.chain = self.w3.net.version
            self.account_number = f"{self.chain} - {str(self.wallet_address)[-8:]}"
            logger.debug("Account {}", self.account_number)
            self.contract_utils = ContractUtils(
                w3=self.w3,
                abi_url=self.abi_url,
                token_mainnet_list=self.token_mainnet_list,
                token_testnet_list=self.token_testnet_list,
                token_personal_list=self.token_personal_list,
                headers=self.headers,
                block_explorer_url=self.block_explorer_url,
                block_explorer_api=self.block_explorer_api,
            )
            self.account = AccountUtils(
                w3=self.w3,
                contract_utils=self.contract_utils,
                wallet_address=self.wallet_address,
                private_key=self.private_key,
                trading_asset_address=self.trading_asset_address,
                router_contract_addr=self.router_contract_addr,
                block_explorer_url=self.block_explorer_url,
                block_explorer_api=self.block_explorer_api,
            )

        if self.follow_wallet:
            if self.w3 and self.follow_wallet_address:
                try:
                    self.wallet_monitor = WalletMonitor(
                        w3=self.w3,
                        address_to_monitor=self.follow_wallet_address
                    )
                    logger.info(
                        f"Wallet monitoring activated for {self.follow_wallet_address} "
                        f"on chain {self.chain}"
                    )
                    self._monitor_task = asyncio.create_task(
                        self._run_monitoring_loop()
                    )
                    logger.info("Wallet monitoring loop started.")
                except ValueError as e:
                    logger.warning(f"Could not initialize WalletMonitor: {e}")
                    self.wallet_monitor = None
                except Exception as e:
                    logger.error(f"Unexpected error initializing WalletMonitor: {e}")
                    self.wallet_monitor = None
            elif not self.w3:
                logger.warning(
                    "Wallet monitoring enabled, but RPC connection failed "
                    "(w3 is None). Monitoring disabled."
                )
                self.wallet_monitor = None
            else:
                logger.warning(
                    "follow_wallet_address is not set."
                    "Monitoring disabled."
                )
                self.wallet_monitor = None
        else:
            self.wallet_monitor = None

    async def _run_monitoring_loop(self):
        logger.info("Entering monitoring loop...")
        if not self.wallet_monitor:
            logger.error(
                "Attempted to run WalletMonitor loop, but not initialized."
            )
            return

        try:
            async for tx in self.wallet_monitor.start_monitoring():
                logger.debug(f"Received transaction {tx.hash.hex()} from monitor.")
                try:
                    asyncio.create_task(self._handle_monitored_transaction(tx))
                except Exception as handler_ex:
                    logger.error(
                        f"Error scheduling handler for tx {tx.hash.hex()}: {handler_ex}"
                    )
        except Exception as loop_ex:
            logger.error(f"Exception in monitoring loop: {loop_ex}")
            # Consider restart logic or specific error handling here
        finally:
            logger.info("Exiting monitoring loop.")

    async def _handle_monitored_transaction(self, tx: TxData):
        tx_hash = tx.hash.hex()
        logger.info(f"Handling monitored transaction: {tx_hash}")

        # Step 1: Filter by target contract
        if not self.router_contract_addr or not tx.to:
            logger.debug(f"[{tx_hash}] No router address or tx.to. Skipping.")
            return
        if Web3.to_checksum_address(tx.to) != self.router_contract_addr:
            logger.debug(
                f"[{tx_hash}] Transaction is not for this client's router "
                f"({self.router_contract_addr}). Skipping."
            )
            return

        # Step 2 & 3: Get Router ABI and Decode Input
        try:
            router_helper = await self.contract_utils.get_data(
                contract_address=self.router_contract_addr
            )
            if not router_helper or not router_helper.abi:
                logger.error(
                    f"[{tx_hash}] Could not fetch ABI for router "
                    f"{self.router_contract_addr}. Cannot decode."
                )
                return

            router_contract = self.w3.eth.contract(
                address=self.router_contract_addr, abi=router_helper.abi
            )
            func_obj, func_params = router_contract.decode_function_input(tx.input)
            logger.debug(f"[{tx_hash}] Decoded function: {func_obj.fn_name}")

        except ValueError as decode_error: # If input doesn't match ABI
            logger.debug(
                f"[{tx_hash}] Could not decode input data: {decode_error}. "
                f"Likely not a target function call."
            )
            return
        except Exception as e:
            logger.error(f"[{tx_hash}] Error getting ABI or decoding input: {e}")
            return

        # Step 4 & 5: Identify Swap Function and Extract Parameters
        # Check against the configurable list of functions
        if func_obj.fn_name in self.follow_wallet_functions:
            # Assuming UniswapV2/PancakeSwap style path parameter for now
            # TODO: Add more robust parameter extraction for different functions
            try:
                path = func_params.get('path')
                if not path or len(path) < 2:
                    logger.warning(
                        f"[{tx_hash}] Invalid or missing 'path' parameter in "
                        f"{func_obj.fn_name}: {path}"
                    )
                    return

                sell_token_address = path[0]
                buy_token_address = path[-1]
                logger.info(
                    f"[{tx_hash}] Identified target function {func_obj.fn_name}: "
                    f"Sell {sell_token_address} -> Buy {buy_token_address}"
                )

            except KeyError as param_error:
                logger.warning(
                    f"[{tx_hash}] Missing expected parameters (like 'path') "
                    f"in {func_obj.fn_name}: {param_error}"
                )
                return
        else:
            logger.debug(
                f"[{tx_hash}] Function {func_obj.fn_name} not in configured list "
                f"{self.follow_wallet_functions}. Skipping."
            )
            return

        # Step 6 & 7: Get Token Symbols and Prepare Arguments
        try:
            sell_token_obj = await self.contract_utils.get_data(
                contract_address=sell_token_address
            )
            buy_token_obj = await self.contract_utils.get_data(
                contract_address=buy_token_address
            )

            if not sell_token_obj or not sell_token_obj.symbol:
                logger.error(
                    f"[{tx_hash}] Could not get symbol for sell token "
                    f"{sell_token_address}"
                )
                return
            if not buy_token_obj or not buy_token_obj.symbol:
                logger.error(
                    f"[{tx_hash}] Could not get symbol for buy token "
                    f"{buy_token_address}"
                )
                return

            sell_symbol = sell_token_obj.symbol
            buy_symbol = buy_token_obj.symbol
            quantity = self.trading_risk_amount # Use configured risk amount

            logger.info(
                f"[{tx_hash}] Preparing copy trade: SELL {quantity} (risk amount) "
                f"of {sell_symbol} for {buy_symbol}"
            )

        except Exception as data_error:
            logger.error(f"[{tx_hash}] Error getting token data for swap: {data_error}")
            return

        # Step 8: Execute Swap via existing get_swap method
        try:
            # TODO: Optimize: Consider modifying get_swap to accept
            #       sell_token_obj and buy_token_obj directly
            #       to avoid redundant symbol lookups within get_swap.
            logger.info(f"[{tx_hash}] Executing copy trade via self.get_swap...")
            swap_result = await self.get_swap(
                sell_token=sell_symbol,
                buy_token=buy_symbol,
                quantity=quantity
            )
            logger.info(f"[{tx_hash}] Copy trade result: {swap_result}")

        except Exception as swap_error:
            logger.error(
                f"[{tx_hash}] Error copy trade for {sell_symbol}->{buy_symbol}: "
                f"{swap_error}"
            )

    async def resolve_token(self, **kwargs):
        """
        A function to resolve a token based on the input address or symbol.
        It takes *args and **kwargs as input parameters.
        Returns the data associated with the token.

        Args:
            **kwargs: either an address or a symbol.

        Returns:
            Token: The token object containing the data if contract_address is provided.
            None: If neither symbol nor contract_address is provided.
        """
        logger.debug("Resolving token {}", kwargs)
        try:
            (identifier,) = kwargs.values()
        except ValueError as e:
            raise ValueError(
                "Token identification must be an address or a symbol"
            ) from e

        # Determine if the input is an address or a symbol
        # Assuming addresses start with '0x'
        if identifier.startswith("0x"):
            result = await self.contract_utils.get_data(contract_address=identifier)
        else:
            symbol = await self.replace_instrument(identifier)
            result = await self.contract_utils.get_data(symbol=symbol)

        # Check if the result is not None
        if not result:
            raise ValueError("Token {} not found", identifier)

        return result

    async def replace_instrument(self, instrument):
        """
        Replace instrument by an alternative instrument, if the
        instrument is not in the mapping, it will be ignored.
        Mapping, define in settings as TOML or .env variable.
        It is a list of dictionaries such as:
        mapping = [
            { id = "BTC", alt = "WBTC" ,enable = true },
        ]

        Args:
            instrument (str):

        Returns:
            dict
        """
        logger.debug("Replace instrument: {}", instrument)
        if self.mapping is None:
            return instrument
        for item in self.mapping:
            if item["id"] == instrument:  # and item["enable"] is not False:
                instrument = item["alt"]
                logger.debug("Instrument symbol changed {}", instrument)
                break
        logger.debug("Instrument symbol changed {}", instrument)
        return instrument

    async def get_order_amount(
        self, sell_token, wallet_address, quantity, is_percentage=True
    ):
        """
        Calculate the order amount based on the sell token,
        wallet address, quantity, and whether it is a percentage.

        Args:
            sell_token (SellToken): The sell token object.
            wallet_address (str): The wallet address.
            quantity (float): The quantity of the sell token.
            is_percentage (bool, optional):
            Flag indicating whether the quantity is a percentage. Defaults to True.

        Returns:
            float: The calculated order amount.
        """
        logger.debug("get order amount {} {} {}", sell_token, wallet_address, quantity)
        logger.debug("Protocol", self.contract_utils.platform)
        balance = await sell_token.get_token_balance(wallet_address)
        logger.debug("Balance {}", balance)
        if not is_percentage and balance:
            logger.debug("Quantity {}", quantity)
            return quantity

        if balance:
            risk_percentage = float(quantity) / 100
            logger.debug("Risk percentage {}", risk_percentage)
            amount = balance * decimal.Decimal(risk_percentage)
            logger.debug("Amount {}", amount)
            if (
                isinstance(amount, decimal.Decimal)
                and amount > self.trading_amount_threshold
            ):
                logger.debug("Amount {}", amount)
                return amount

        return 0

    async def get_quote(
        self,
        buy_address=None,
        buy_symbol=None,
        sell_address=None,
        sell_symbol=None,
        amount=1,
    ):
        """
        Get a quote method for specific protocol

        """

    async def get_swap(self, sell_token=None, buy_token=None, quantity=1):
        """
        Execute a swap

        Args:
            sell_token (str): The sell token.
            buy_token (str): The buy token.
            quantity (int): The quantity of tokens.

        Returns:
            transactionHash


        """
        try:
            logger.debug("get swap {} {} {}", sell_token, buy_token, quantity)
            logger.debug("Protocol", self.contract_utils.platform)
            sell_token = await self.contract_utils.get_data(symbol=sell_token)
            logger.debug("sell token {}", sell_token)
            buy_token = await self.contract_utils.get_data(symbol=buy_token)
            logger.debug("buy token {}", buy_token)

            sell_amount = await self.get_order_amount(
                sell_token, self.account.wallet_address, quantity
            )
            if not sell_amount or sell_amount == 0:
                logger.error("sell amount {}", sell_amount)
                return f"⚠️ sell amount failed {sell_amount}"

            sell_token_amount_wei = decimal.Decimal(sell_amount) * (
                decimal.Decimal("10") ** int(sell_token.decimals)
            )
            if self.protocol == "0x":
                await self.account.get_approve(sell_token.address)

            order_amount = int(
                sell_token_amount_wei * decimal.Decimal((self.trading_slippage / 100))
            )
            logger.debug("order amount {}", order_amount)

            order = await self.make_swap(
                sell_token.address, buy_token.address, order_amount
            )

            if not order:
                logger.error("swap order not executed")
                return "⚠️ order execution failed"

            signed_order = await self.account.get_sign(order)
            order_hash = str(self.w3.to_hex(signed_order))
            logger.debug(order_hash)
            receipt = self.w3.eth.wait_for_transaction_receipt(order_hash)
            logger.debug(receipt)

            if receipt["status"] != 1:
                logger.error("receipt failed")

            return await self.contract_utils.get_confirmation(
                receipt["transactionHash"]
            )

        except Exception as error:
            logger.debug(error)
            return f"⚠️ {str(error)}"

    async def make_swap(self, sell_address, buy_address, amount):
        """
        Make a swap method for specific protocol

        """

    async def get_account_balance(self):
        """
        Retrieves the account balance.

        :return: The account balance.
        :rtype: float
        """
        return await self.account.get_account_balance()

    async def get_trading_asset_balance(self):
        """
        Retrieves the trading asset balance for the current account.

        :return: A dictionary containing the trading asset balance.
                The dictionary has the following keys:
                - 'asset': The asset symbol.
                - 'free': The free balance of the asset.
                - 'locked': The locked balance of the asset.
        """
        return await self.account.get_trading_asset_balance()

    async def get_account_position(self):
        """
        Retrieves the account position.

        :return: The account position.
        :rtype: AccountPosition
        """
        return await self.account.get_account_position()

    async def get_account_margin(self):
        """
        Retrieves the account margin.

        :return: The account margin.
        :rtype: float
        """
        return await self.account.get_account_margin()

    async def get_account_open_positions(self):
        """
        Retrieves the open positions of the account.

        :return: A list of open positions in the account.
        """
        return await self.account.get_account_open_positions()

    async def get_account_pnl(self, period=None):
        """
        Return account pnl.

        Args:
            None

        Returns:
            pnl
        """
        today = datetime.now().date()
        if period is None:
            start_date = today
        elif period == "W":
            start_date = today - timedelta(days=today.weekday())
        elif period == "M":
            start_date = today.replace(day=1)
        elif period == "Y":
            start_date = today.replace(month=1, day=1)
        else:
            return 0
        return self.calculate_pnl(start_date) if self.is_pnl_active else 0

    async def calculate_pnl(self, period=None):
        """
        Calculate the PnL for a given period.
        via https://rotki.readthedocs.io/en/latest/api.html

        Parameters:
            period (str):
            The period for which to calculate PnL ('W', 'M', 'Y', or None)

        Returns:
            pnl: The calculated PnL value.
        """

        if self.rotki_report_endpoint is None:
            return 0
        params = {"period": period} if period else {}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.rotki_report_endpoint, params=params
            ) as response:
                if response.status != 200:
                    logger.error(f"Received non-200 status code: {response.status}")
                    return 0
                data = await response.json()
                result = data.get("result", {})
                entries = result.get("entries", [])
                # Initialize a dictionary to hold the sum of 'free' values
                free_values = {
                    "trade": 0,
                    "transaction event": 0,
                    "fee": 0,
                    "asset movement": 0,
                }
                for entry in entries:
                    overview = entry.get("overview", {})
                    for category, amounts in overview.items():
                        try:
                            free_amount = float(amounts.get("free", "0"))
                            # Add it to the total
                            free_values[category] += free_amount
                        except ValueError:
                            logger.error(f"Invalid free amount: {amounts.get('free')}")

                return free_values
