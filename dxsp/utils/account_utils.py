"""
 DEX SWAP
🔒 USER RELATED
"""

from loguru import logger


class AccountUtils:
    """
    Class AccountUtils to interact with private related methods
    such as account balance, signing transactions, etc.

    Args:
        None

    Methods:

        get_account_balance()
        get_trading_asset_balance()
        get_account_position
        get_account_margin
        get_account_open_positions
        get_account_pnl
        get_approve
        get_sign
        get_gas
        get_gas_price

    """

    def __init__(self, **kwargs):
        get = kwargs.get

        self.w3 = self.w3 = get("w3", None)
        self.wallet_address = self.w3.to_checksum_address(
            get("wallet_address", None)
        )
        self.account_number = (
            f"{int(self.w3.net.version, 16)} - " f"{str(self.wallet_address)[-8:]}"
        )
        self.private_key = get("private_key", None)
        self.trading_asset_address = self.w3.to_checksum_address(
            get("trading_asset_address", None)
        )
        self.router_contract_addr = get("router_contract_addr", None)
        self.contract_utils = get("contract_utils", None)
        self.block_explorer_url = get("block_explorer_url", None)
        self.block_explorer_api = get("block_explorer_api", None)

    async def get_account_balance(self) -> str:
        """
        Retrieves the account balance of the user.

        Returns:
            A formatted string containing
            the account balance in Bitcoin (₿) and
            the trading asset balance like USDT (💵).
        """
        account_balance = self.w3.from_wei(
            self.w3.eth.get_balance(self.wallet_address), "ether"
        )
        trading_asset_balance = await self.get_trading_asset_balance()
        return (
            f"{self.account_number} \n"
            f"₿: {account_balance:.5f}\n"
            f"💵: {trading_asset_balance:.2f}"
        )

    async def get_trading_asset_balance(self) -> float:
        """
        Retrieves the balance of the trading asset
        for the current wallet address.

        Returns:
            The balance of the trading asset as a float.
        """
        trading_asset = await self.contract_utils.get_data(
            contract_address=self.trading_asset_address
        )
        balance = await trading_asset.get_token_balance(self.wallet_address)
        return balance or 0.0

    async def get_account_position(self) -> str:
        """
        Retrieves the account position.

        Returns:
            A string representing the account position.
        """
        opened_positions = await self.get_account_open_positions()
        margin = await self.get_account_margin()
        return (
            f"📊 {self.account_number} \n"
            f"Opened: {opened_positions}\n"
            f"Margin: {margin}"
        )

    async def get_account_margin(self):
        """
        Get the account margin. Not yet implemented

        Returns:
            int: The account margin.
        """
        return 0

    async def get_account_open_positions(self):
        """
        Get the open positions for the account.
        Not yet implemented

        :return: The number of open positions
        for the account.
        """
        return 0

    async def get_account_pnl(self):
        """
        Get the open positions for the account.
        Not yet implemented

        :return: The number of open positions
        for the account.
        """
        return f"{self.account_number}: 0"

    async def get_approve(self, token_address):
        """
        Given a token address, approve a token

        Args:
            token_address (str): The token address

        Returns:
            approval_tx_hash

        """
        try:
            token = await self.contract_utils.get_data(contract_address=token_address)
            if token.contract is None:
                return
            approved_amount = self.w3.to_wei(2**64 - 1, "ether")
            owner_address = self.w3.to_checksum_address(self.wallet_address)
            dex_router_address = self.w3.to_checksum_address(self.router_contract_addr)
            allowance = token.contract.functions.allowance(
                owner_address, dex_router_address
            ).call()
            if allowance == 0:
                approval_tx = token.contract.functions.approve(
                    dex_router_address, approved_amount
                )
                approval_tx_hash = await self.get_sign(approval_tx.transact())
                return self.w3.eth.wait_for_transaction_receipt(approval_tx_hash)
        except Exception as error:
            logger.error("Approval failed {}", error)

    async def get_sign(self, transaction):
        """
        Given a transaction, sign a transaction

        Args:
            transaction (Transaction): The transaction

        Returns:
            signed_tx_hash

        """
        try:
            signed_tx = self.w3.eth.account.sign_transaction(
                transaction, self.private_key
            )
            return self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        except Exception as error:
            logger.error("Sign failed {}", error)

    async def get_gas(self, transaction):
        """
        Given a transaction, get gas estimate

        Args:
            transaction (Transaction): The transaction

        Returns:
            int: The gas estimate

        """
        gas_limit = self.w3.eth.estimate_gas(transaction) * 1.25
        return int(self.w3.to_wei(gas_limit, "wei"))

    async def get_gas_price(self):
        """
        search get gas price

        Returns:
            int: The gas price

        """

        return round(self.w3.from_wei(self.w3.eth.generate_gas_price(), "gwei"), 2)
