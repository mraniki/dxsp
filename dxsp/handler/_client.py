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
    """Handles interactions with decentralized exchanges (DEXs).

    Manages connections to DEXs, handles token resolution, order amount
    calculations, swaps, and account information retrieval. Supports
    monitoring a wallet for specific transactions and mirroring those trades.

    Attributes:
        name (str | None): Optional name for the client instance.
        protocol (str): The DEX protocol library to use (e.g., "uniswap", "0x").
        protocol_version (int): The version of the protocol library.
        api_endpoint (str | None): API endpoint for the DEX (if applicable).
        api_key (str | None): API key for the DEX (if applicable).
        rpc (str | None): RPC URL for the blockchain node.
        w3 (Web3 | None): Web3 instance for blockchain interaction.
        wallet_address (str | None): The wallet address to use for trading.
        private_key (str | None): The private key for the wallet address.
        headers (dict): Headers for HTTP requests (e.g., to ABI URLs).
        abi_url (str): URL to fetch the standard ERC20 ABI.
        token_mainnet_list (str | None): Path to a list of mainnet tokens.
        token_testnet_list (str | None): Path to a list of testnet tokens.
        token_personal_list (str | None): Path to a personal list of tokens.
        router_contract_addr (str | None): Address of the DEX router contract.
        factory_contract_addr (str | None): Address of the DEX factory contract.
        trading_asset_address (str | None): Address of the primary trading asset (e.g., WETH, USDC).
        trading_risk_percentage (float | None): Default risk percentage per trade.
        trading_asset_separator (str | None): Separator used in instrument names (e.g., '-').
        trading_risk_amount (decimal.Decimal | None): Default fixed risk amount per trade.
        trading_slippage (float | None): Allowed slippage percentage for swaps.
        trading_amount_threshold (decimal.Decimal | None): Minimum amount threshold for trades.
        block_explorer_url (str | None): URL of the blockchain explorer.
        block_explorer_api (str | None): API URL for the blockchain explorer.
        mapping (list[dict] | None): Mapping for replacing instrument symbols.
        is_pnl_active (bool): Flag to enable/disable PnL calculation.
        rotki_report_endpoint (str | None): URL for the Rotki PnL reporting endpoint.
        follow_wallet (bool): Flag to enable/disable wallet monitoring.
        follow_wallet_address (str | None): Address of the wallet to monitor.
        follow_wallet_functions (list[str]): List of function names to monitor
            (e.g., ['swapExactTokensForTokens']).
        client: Placeholder for potential DEX-specific client object.
        chain (str | None): Chain ID derived from the RPC connection.
        account_number (str | None): Identifier for the account (chain ID + partial address).
        contract_utils (ContractUtils | None): Utility for contract interactions.
        account (AccountUtils | None): Utility for account management.
        wallet_monitor (WalletMonitor | None): Instance for monitoring wallet transactions.
        _monitor_task (asyncio.Task | None): Task handle for the monitoring loop.
    """

    def __init__(self, **kwargs):
        """Initializes the DexClient with configuration parameters.

        Sets up Web3 connection, contract/account utilities, and optionally
        starts the wallet monitoring feature based on the provided keyword
        arguments.

        Args:
            **kwargs: Keyword arguments for configuration. See class docstring
                for a list of supported parameters.
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
        self.follow_wallet_functions = get("follow_wallet_functions", ["swapExactTokensForTokens"])

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
                logger.debug(f"Chain {self.w3.net.version} - {int(self.w3.net.version, 16)}")
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
                        w3=self.w3, address_to_monitor=self.follow_wallet_address
                    )
                    logger.info(
                        f"Wallet monitoring activated for {self.follow_wallet_address} "
                        f"on chain {self.chain}"
                    )
                    self._monitor_task = asyncio.create_task(self._run_monitoring_loop())
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
                logger.warning("follow_wallet_address is not set.Monitoring disabled.")
                self.wallet_monitor = None
        else:
            self.wallet_monitor = None

    async def _run_monitoring_loop(self):
        """Runs the wallet monitoring loop asynchronously.

        Listens for new transactions from the `WalletMonitor` instance
        and schedules `_handle_monitored_transaction` for processing each
        relevant transaction. Handles exceptions during the loop.
        """
        logger.info("Entering monitoring loop...")
        if not self.wallet_monitor:
            logger.error("Attempted to run WalletMonitor loop, but not initialized.")
            return

        try:
            async for tx in self.wallet_monitor.start_monitoring():
                logger.debug(f"Received transaction {tx.hash.hex()} from monitor.")
                try:
                    asyncio.create_task(self._handle_monitored_transaction(tx))
                except Exception as handler_ex:
                    logger.error(f"Error scheduling handler for tx {tx.hash.hex()}: {handler_ex}")
        except Exception as loop_ex:
            logger.error(f"Exception in monitoring loop: {loop_ex}")
            # Consider restart logic or specific error handling here
        finally:
            logger.info("Exiting monitoring loop.")

    async def _handle_monitored_transaction(self, tx: TxData):
        """Processes a transaction from the monitored wallet.

        This method processes a transaction received from the
        `WalletMonitor` instance. It filters transactions by the
        configured router contract address, decodes the function call,
        identifies the target function, and prepares arguments for a swap.

        Args:
            tx (TxData): The transaction data to process.

        Returns:
            None. The method returns early if the transaction is filtered out
            or if errors occur during processing. It triggers a swap via
            `get_swap` if a valid monitored transaction is identified.
        """
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

        except ValueError as decode_error:  # If input doesn't match ABI
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
                path = func_params.get("path")
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
            sell_token_obj = await self.contract_utils.get_data(contract_address=sell_token_address)
            buy_token_obj = await self.contract_utils.get_data(contract_address=buy_token_address)

            if not sell_token_obj or not sell_token_obj.symbol:
                logger.error(
                    f"[{tx_hash}] Could not get symbol for sell token {sell_token_address}"
                )
                return
            if not buy_token_obj or not buy_token_obj.symbol:
                logger.error(f"[{tx_hash}] Could not get symbol for buy token {buy_token_address}")
                return

            sell_symbol = sell_token_obj.symbol
            buy_symbol = buy_token_obj.symbol
            quantity = self.trading_risk_amount  # Use configured risk amount

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
                sell_token=sell_symbol, buy_token=buy_symbol, quantity=quantity
            )
            logger.info(f"[{tx_hash}] Copy trade result: {swap_result}")

        except Exception as swap_error:
            logger.error(
                f"[{tx_hash}] Error copy trade for {sell_symbol}->{buy_symbol}: {swap_error}"
            )

    async def resolve_token(self, identifier: str):
        """Resolves a token identifier (symbol or address) to token data.

        Uses `ContractUtils` to fetch token information based on whether the
        identifier is recognized as a contract address (starts with '0x')
        or a token symbol. Applies instrument mapping if applicable.

        Args:
            identifier (str): The token symbol (e.g., "WETH") or contract
                address (e.g., "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2").

        Returns:
            ContractData: An object containing token details (address, symbol,
                decimals, ABI, etc.) from `ContractUtils`.

        Raises:
            ValueError: If the token identifier cannot be resolved.
        """
        logger.debug("Resolving token {}", identifier)
        # try:
        #     (identifier,) = kwargs.values()
        # except ValueError as e:
        #     raise ValueError("Token identification must be an address or a symbol") from e

        # Determine if the input is an address or a symbol
        # Assuming addresses start with '0x'
        if identifier.startswith("0x"):
            result = await self.contract_utils.get_data(contract_address=identifier)
        else:
            symbol = await self.replace_instrument(identifier)
            result = await self.contract_utils.get_data(symbol=symbol)

        # Check if the result is not None
        if not result:
            raise ValueError(f"Token {identifier} not found")

        return result

    async def replace_instrument(self, instrument: str) -> str:
        """Replaces an instrument symbol using the configured mapping.

        Checks if the `self.mapping` list contains an entry for the given
        `instrument` and returns the corresponding alternative symbol (`alt`)
        if found and enabled. Otherwise, returns the original instrument.

        Args:
            instrument (str): The instrument symbol to potentially replace.

        Returns:
            str: The replaced instrument symbol or the original symbol if no
                 mapping is found or applicable.
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
        self, sell_token, wallet_address: str, quantity: float | decimal.Decimal,
        is_percentage: bool = True
    ) -> decimal.Decimal:
        """Calculates the order amount in the sell token's base units.

        Calculates the amount based on a percentage of the wallet's balance
        of the `sell_token` or a fixed `quantity`.

        Args:
            sell_token: The `ContractData` object for the token being sold.
            wallet_address (str): The address of the wallet holding the token.
            quantity (float | decimal.Decimal): The percentage (e.g., 1 for 1%)
                or the fixed amount of the token to sell.
            is_percentage (bool): If True, `quantity` is treated as a percentage
                of the balance. If False, `quantity` is a fixed amount.

        Returns:
            decimal.Decimal: The calculated order amount in the token's base
                units, or Decimal(0) if the balance is insufficient or zero.
        """
        logger.debug("get order amount {} {} {}", sell_token.symbol, wallet_address, quantity)
        logger.debug("Protocol {}", self.contract_utils.platform)
        balance = await sell_token.get_token_balance(wallet_address)
        logger.debug("Balance {} {}", balance, sell_token.symbol)

        if not balance or balance == 0:
            logger.warning("Balance is zero for {}", sell_token.symbol)
            return decimal.Decimal(0)

        if not is_percentage:
            # If quantity is fixed, return it directly if balance is sufficient
            fixed_amount = decimal.Decimal(quantity)
            if balance >= fixed_amount:
                logger.debug("Using fixed quantity: {} {}", fixed_amount, sell_token.symbol)
                return fixed_amount
            else:
                logger.warning(
                    f"Insufficient balance ({balance} {sell_token.symbol}) "
                    f"for fixed quantity ({fixed_amount} {sell_token.symbol})"
                )
                return decimal.Decimal(0)

        # Calculate amount based on percentage
        risk_percentage = decimal.Decimal(quantity) / 100
        logger.debug("Risk percentage {}", risk_percentage)
        amount = balance * risk_percentage
        logger.debug("Calculated amount {} {}", amount, sell_token.symbol)

        # Check against threshold (assuming threshold is in the token's units, not wei)
        # TODO: Clarify if trading_amount_threshold is in native units or wei
        threshold = self.trading_amount_threshold or decimal.Decimal(0)
        if amount > threshold:
            logger.debug("Amount {} > Threshold {}", amount, threshold)
            return amount
        else:
            logger.warning(
                f"Calculated amount {amount} {sell_token.symbol} is below "
                f"threshold {threshold}"
             )
            return decimal.Decimal(0)

    async def get_quote(
        self,
        buy_address: str | None = None,
        buy_symbol: str | None = None,
        sell_address: str | None = None,
        sell_symbol: str | None = None,
        amount: int = 1,
    ):
        """Fetches a quote for a potential swap (Not Implemented).

        Args:
            buy_address (str | None): Contract address of the token to buy.
            buy_symbol (str | None): Symbol of the token to buy.
            sell_address (str | None): Contract address of the token to sell.
            sell_symbol (str | None): Symbol of the token to sell.
            amount (int): The amount of the sell token (in its base unit)
                for the quote. Defaults to 1.

        Returns:
            NotImplemented: This method is not yet implemented.
        """
        pass

    async def get_swap(
        self, sell_token: str | None = None, buy_token: str | None = None,
        quantity: float | decimal.Decimal = 1
    ) -> str:
        """Executes a swap between two tokens using specified symbols.

        Resolves token symbols to addresses, calculates the order amount
        based on the configured risk settings (percentage or fixed amount),
        approves the router contract if necessary (e.g., for 0x protocol),
        constructs and executes the swap transaction, waits for the receipt,
        and returns a confirmation message or error.

        Args:
            sell_token (str | None): Symbol of the token to sell (e.g., "WETH").
            buy_token (str | None): Symbol of the token to buy (e.g., "USDC").
            quantity (float | decimal.Decimal): The quantity or percentage
                to swap, interpreted based on `trading_risk_percentage` vs
                `trading_risk_amount` settings. Defaults to 1 (interpreted
                based on config).

        Returns:
            str: A confirmation message with the transaction hash on success,
                 or an error message string starting with "⚠️" on failure.
        """
        try:
            # Determine quantity and if it's a percentage based on config
            is_percentage = self.trading_risk_percentage is not None
            trade_quantity = (
                self.trading_risk_percentage if is_percentage else self.trading_risk_amount
            )
            if trade_quantity is None:
                 # Fallback if neither percentage nor amount is set
                 logger.warning(
                     "Neither trading_risk_percentage nor trading_risk_amount is set. "
                     "Defaulting to quantity=1 as percentage."
                 )
                 trade_quantity = decimal.Decimal(1)
                 is_percentage = True
            else:
                trade_quantity = decimal.Decimal(trade_quantity)


            logger.debug(
                f"get swap: Sell {sell_token}, Buy {buy_token}, "
                f"Quantity Arg: {quantity} -> Using Config: {trade_quantity} "
                f"{'%' if is_percentage else ''}"
            )
            logger.debug("Protocol {}", self.contract_utils.platform)

            # Resolve tokens
            sell_token_obj = await self.resolve_token(identifier=sell_token)
            logger.debug("Sell token data: {}", sell_token_obj)
            buy_token_obj = await self.resolve_token(identifier=buy_token)
            logger.debug("Buy token data: {}", buy_token_obj)

            # Calculate order amount in sell token's native units
            sell_amount_native = await self.get_order_amount(
                sell_token_obj, self.account.wallet_address, trade_quantity, is_percentage
            )

            if not sell_amount_native or sell_amount_native == 0:
                logger.error("Calculated sell amount is zero or failed: {}", sell_amount_native)
                return "⚠️ Sell amount calculation failed or resulted in zero."

            logger.info(f"Calculated sell amount: {sell_amount_native} {sell_token_obj.symbol}")

            # Convert native amount to Wei
            sell_token_amount_wei = int(
                sell_amount_native * (decimal.Decimal("10") ** int(sell_token_obj.decimals))
            )
            logger.debug(f"Sell amount in Wei: {sell_token_amount_wei}")


            # Approve router if needed (e.g., 0x)
            if self.protocol == "0x":
                logger.info(f"Approving router for {sell_token_obj.symbol}...")
                await self.account.get_approve(sell_token_obj.address)
                logger.info("Approval likely sent (check logs/explorer).")


            # TODO: Slippage calculation might need refinement depending on protocol
            # This looks like it's applying slippage *before* getting the quote/swap params.
            # Usually, slippage is applied *after* getting a quote to set a minimum receive amount.
            # Renaming `order_amount` to `amount_in_wei_for_swap` for clarity.
            # The actual amount used in the swap call might differ based on the protocol.
            # For UniV2 swapExactTokens*, this is `amountIn`.
            amount_in_wei_for_swap = sell_token_amount_wei
            # amount_min_out = int(
            #    sell_token_amount_wei * decimal.Decimal(1 - (self.trading_slippage / 100))
            # ) # Example slippage calc
            # logger.debug("Slippage adjusted min out (example): {}", amount_min_out)
            logger.debug("Amount for swap function (amountIn): {}", amount_in_wei_for_swap)

            # Make the swap transaction
            order = await self.make_swap(
                sell_token_obj.address, buy_token_obj.address, amount_in_wei_for_swap
            )

            if not order:
                logger.error("Swap order creation/fetch failed in make_swap.")
                return "⚠️ Order creation/fetch failed."

            # Sign and send transaction
            signed_tx_hash = await self.account.get_sign(order) # Assuming get_sign returns the hash
            # signed_order = await self.account.get_sign(order) # If get_sign returns signed tx
            # order_hash = str(
            #     self.w3.eth.send_raw_transaction(signed_order.rawTransaction).hex()
            # ) # If signing locally

            logger.info(f"Transaction submitted: {signed_tx_hash}")

            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(signed_tx_hash)
            logger.debug("Transaction receipt: {}", receipt)

            if receipt["status"] != 1:
                logger.error(f"Transaction failed! Receipt: {receipt}")
                # Consider returning more info from receipt if available
                return f"⚠️ Transaction failed (Status 0). Hash: {signed_tx_hash}"

            # Return confirmation (e.g., explorer link)
            confirmation = await self.contract_utils.get_confirmation(receipt["transactionHash"])
            logger.info(f"Swap successful: {confirmation}")
            return confirmation

        except ValueError as ve:
             logger.error(f"Value error during swap: {ve}")
             return f"⚠️ {str(ve)}"
        except Exception as error:
            # Use exception for stack trace
            logger.exception(f"Unexpected error during swap: {error}")
            return f"⚠️ Unexpected error: {str(error)}"

    async def make_swap(self, sell_address: str, buy_address: str, amount: int):
        """Constructs the swap transaction data (Not Implemented).

        This method should interact with the specific DEX protocol's API or
        contracts to prepare the transaction parameters for a swap.

        Args:
            sell_address (str): Contract address of the token to sell.
            buy_address (str): Contract address of the token to buy.
            amount (int): The amount of the sell token in Wei.

        Returns:
            NotImplemented: This method is not yet implemented.
            Should return the transaction data (e.g., dict for web3 `send_transaction`).
        """
        pass

    async def get_account_balance(self) -> str | None:
        """Fetches the native balance (e.g., ETH, BNB) of the client's wallet.

        Returns:
            str | None: The native balance as a string, or None if unavailable.
        """
        return await self.account.get_account_balance()

    async def get_trading_asset_balance(self) -> str | None:
        """Fetches the balance of the configured `trading_asset_address`.

        Returns:
            str | None: The trading asset balance as a string, or None if
                unavailable or not configured.
        """
        return await self.account.get_trading_asset_balance()

    async def get_account_position(self):
        """Fetches the account's overall position (Not Implemented in AccountUtils).

        Returns:
            NotImplemented: Depends on the implementation in `AccountUtils`.
        """
        return await self.account.get_account_position()

    async def get_account_margin(self):
        """Fetches the account's margin details (Not Implemented in AccountUtils).

        Returns:
            NotImplemented: Depends on the implementation in `AccountUtils`.
        """
        return await self.account.get_account_margin()

    async def get_account_open_positions(self):
        """Fetches the account's open positions (Not Implemented in AccountUtils).

        Returns:
            NotImplemented: Depends on the implementation in `AccountUtils`.
        """
        return await self.account.get_account_open_positions()

    async def get_account_pnl(self, period: str | None = None) -> float | dict:
        """Calculates Profit and Loss (PnL) for the account for a given period.

        Delegates the calculation to `calculate_pnl` if PnL tracking is active.
        Determines the start date based on the `period` identifier.

        Args:
            period (str | None): The period identifier ('W' for week, 'M' for
                month, 'Y' for year, None for today). Defaults to None (today).

        Returns:
            float | dict: The calculated PnL. Returns 0 if PnL is inactive.
                The return type depends on `calculate_pnl` (expected dict or 0).
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

    async def calculate_pnl(self, period: str | None = None) -> dict | int:
        """Calculates PnL by querying the Rotki reporting endpoint.

        Sends a GET request to the configured `rotki_report_endpoint`
        with the optional period parameter. Parses the JSON response
        to extract and sum 'free' amounts from different categories.

        Args:
            period (str | None): The period string to pass to the Rotki API.
                Defaults to None.

        Returns:
            dict | int: A dictionary containing the sum of 'free' PnL values
                per category (e.g., 'trade', 'fee') on success. Returns 0 if
                the endpoint is not configured, the request fails, or the
                response format is unexpected.
        """
        if self.rotki_report_endpoint is None:
            logger.warning("Rotki report endpoint not configured. Cannot calculate PnL.")
            return 0
        params = {"period": period} if period else {}

        async with aiohttp.ClientSession() as session:
            async with session.get(self.rotki_report_endpoint, params=params) as response:
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
