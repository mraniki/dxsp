"""
 DEX SWAP
🔒 USER RELATED
"""
from typing import Optional

from loguru import logger
from web3 import Web3

from dxsp import __version__
from dxsp.config import settings
from dxsp.utils.contract_utils import ContractUtils
from dxsp.utils.explorer_utils import get_account_transactions


class AccountUtils:

    """
    Class AccountUtils to interact with private related methods
    such as account balance, signing transactions, etc.

    Args:
        w3 (Optional[Web3]): Web3

    Methods:
        get_info()
        get_name()
        get_help()
        get_account_balance()
        get_trading_asset_balance()
        get_account_position
        get_account_margin
        get_account_open_positions
        get_account_transactions()
        get_account_pnl
        get_approve
        get_sign
        get_gas
        get_gas_price

    """

    def __init__(self, w3: Optional[Web3] = None):
        self.logger = logger
        self.w3 = w3 or Web3(Web3.HTTPProvider(settings.dex_rpc))
        self.wallet_address = self.w3.to_checksum_address(settings.dex_wallet_address)
        self.account_number = (
            f"{str(self.w3.net.version)} - " f"{str(self.wallet_address)[-8:]}"
        )
        self.private_key = settings.dex_private_key
        self.trading_asset_address = self.w3.to_checksum_address(
            settings.trading_asset_address
        )
        self.contract_utils = ContractUtils(w3=self.w3)
        self.commands = settings.dxsp_commands

    async def get_info(self):
        """
        Get the information about the DexSwap API.

        Returns:
            str: A string containing the version of DexSwap, the name obtained from
                 `get_name()`, and the account number.
        Raises:
            Exception: If there is an error while retrieving the information.
        """
        try:
            return (
                f"ℹ️ DexSwap v{__version__}\n"
                f"💱 {await self.get_name()}\n"
                f"🪪 {self.account_number}"
            )
        except Exception as error:
            return error

    async def get_name(self):
        """
        Retrieves the name of the object being the
        last 8 characters of the router contract address.

        :return: A string representing
        the name of the object.
        """
        if settings.dex_router_contract_addr:
            return str(settings.dex_router_contract_addr)[-8:]

    async def get_help(self):
        """
        Asynchronously retrieves the help information.

        Returns:
            str: The help information,
            including the available commands.
        """
        return f"{self.commands}\n"

    async def get_account_balance(self):
        """
        Retrieves the account balance of the user.

        Returns:
            str: A formatted string containing
            the account balance in Bitcoin (₿) and
            the trading asset balance like USDT (💵).
        """
        account_balance = self.w3.eth.get_balance(
            self.w3.to_checksum_address(self.wallet_address)
        )
        account_balance = self.w3.from_wei(account_balance, "ether") or 0
        trading_asset_balance = await self.get_trading_asset_balance()
        return f"₿ {round(account_balance,5)}\n💵 {trading_asset_balance}"

    async def get_trading_asset_balance(self):
        """
        Retrieves the balance of the trading asset
        for the current wallet address.

        Returns:
            The balance of the trading asset as a float.
            If the balance is not available,
            it returns 0.
        """
        trading_asset_balance = await self.contract_utils.get_token_balance(
            self.trading_asset_address, self.wallet_address
        )
        return trading_asset_balance if trading_asset_balance else 0

    async def get_account_position(self):
        """
        Retrieves the account position.

        Returns:
            str: A string representing the account position.
        """
        position = "📊 Position\n"
        position += f"Opened: {str(await self.get_account_open_positions())}\n"
        position += f"Margin: {str(await self.get_account_margin())}"
        return position

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

    async def get_account_transactions(self, period=24):
        """
        Retrieve the account transactions for a given period.
        Not yet implemented

        Args:
            period (int): The time period in hours
            to retrieve the transactions for.
            Default is 24 hours.

        Returns:
            List[Transaction]: A list of transactions for the account.
        """
        return await get_account_transactions(
            period, self.trading_asset_address, self.wallet_address
        )

    async def get_account_pnl(self, period=24):
        """
        Create a profit and loss (PnL)
        report for the account.
        Not yet implemented

        Args:
            period (int): The time period in hours
            to retrieve the PnL for. Default is 24 hours.

        Returns:
            str: A string containing the PnL report.


        """
        pnl_dict = await self.get_account_transactions(period)
        pnl_report = "".join(
            f"{token} {value}\n" for token, value in pnl_dict["tokenList"].items()
        )
        pnl_report += f"Total {pnl_dict['pnl']}\n"
        pnl_report += await self.get_account_position()

        return pnl_report

    async def get_approve(self, token_address):
        """
        Given a token address, approve a token

        Args:
            token_address (str): The token address

        Returns:
            approval_tx_hash

        """
        try:
            contract = await self.contract_utils.get_token_contract(token_address)
            if contract is None:
                return
            approved_amount = self.w3.to_wei(2**64 - 1, "ether")
            owner_address = self.w3.to_checksum_address(self.wallet_address)
            dex_router_address = self.w3.to_checksum_address(
                settings.dex_router_contract_addr
            )
            allowance = contract.functions.allowance(
                owner_address, dex_router_address
            ).call()
            if allowance == 0:
                approval_tx = contract.functions.approve(
                    dex_router_address, approved_amount
                )
                approval_tx_hash = await self.get_sign(approval_tx.transact())
                return self.w3.eth.wait_for_transaction_receipt(approval_tx_hash)
        except Exception as error:
            raise ValueError(f"Approval failed {error}")

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
            raise error

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
