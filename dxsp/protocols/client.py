"""
Base DexClient Class   🦄
"""


from typing import Optional

from web3 import Web3

from dxsp.utils import AccountUtils, ContractUtils


class DexClient:
    def __init__(
        self,
        w3: Optional[Web3] = None,
        **kwargs,
    ):
        self.wallet_address = kwargs.get("wallet_address")
        self.private_key = kwargs.get("private_key")
        self.protocol_type = kwargs.get("protocol_type", "uniswap")
        self.protocol_version = kwargs.get("protocol_version", 2)
        self.api_endpoint = kwargs.get("api_endpoint", "https://api.0x.org/")
        self.api_key = kwargs.get("api_key")
        self.router = kwargs.get("router")
        self.trading_asset_address = kwargs.get("trading_asset_address")
        self.trading_slippage = kwargs.get("trading_slippage")
        self.block_explorer_url = kwargs.get(
            "block_explorer_url", "https://api.etherscan.io/api?"
        )
        self.block_explorer_api = kwargs.get("block_explorer_api")

        self.w3 = w3
        self.dex_swap = self._get_dex_swap_instance()
        self.wallet_address = self.dex_swap.wallet_address
        self.account = AccountUtils(
            self.w3, self.wallet_address, self.private_key, self.trading_asset_address
        )
        self.contract_utils = ContractUtils(self.w3)

    def _get_dex_swap_instance(self):
        if self.protocol_type == "0x":
            from dxsp.protocols.zerox import DexZeroX

            return DexZeroX()
        elif self.protocol_type == "1inch":
            from dxsp.protocols.oneinch import DexOneInch

            return DexOneInch()
        else:
            from dxsp.protocols.uniswap import DexUniswap

            return DexUniswap()

    async def get_quote(self, buy_address, sell_address, amount=1):
        """ """
        pass

    async def get_swap(self, sell_address, buy_address, amount):
        """ """
        pass

    async def get_name(self):
        """
        Retrieves the name of the account.

        :return: The name of the account.
        """
        return await self.account.get_name()

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

    async def get_account_transactions(self, period=24):
        """
        Get the account transactions
        for a specific period.

        Args:
            period (int): The number of hours
            for which to retrieve the transactions. Defaults to 24.

        Returns:
            List[Transaction]: A list of
            transaction objects representing the account transactions.
        """
        return await self.account.get_account_transactions(period)

    async def get_account_pnl(self, period=24):
        """
        Get the profit and loss (PnL)
        for the account within a specified period.

        Args:
            period (int, optional):
            The period in hours for which to calculate the PnL.
            Defaults to 24.

        Returns:
            float: The profit and loss (PnL)
            for the account within the specified period.
        """
        return await self.account.get_account_pnl(period)
