"""
 DEX SWAP
🔒 USER RELATED
"""
import logging
from typing import Optional

from web3 import Web3

from dxsp import __version__
from dxsp.config import settings
from dxsp.utils.contract_utils import ContractUtils
from dxsp.utils.explorer_utils import get_account_transactions


class AccountUtils:

    def __init__(self, w3: Optional[Web3] = None):
        self.logger = logging.getLogger(name="DexSwap")
        self.w3 = w3 or Web3(Web3.HTTPProvider(settings.dex_rpc))
        self.wallet_address = self.w3.to_checksum_address(
            settings.dex_wallet_address)
        self.account_number = (f"{str(self.w3.net.version)} - "
                        f"{str(self.wallet_address)[-8:]}")
        self.private_key = settings.dex_private_key
        self.trading_asset_address = self.w3.to_checksum_address(
        settings.trading_asset_address)
        self.contract_utils = ContractUtils(w3=self.w3)
        self.commands = settings.dxsp_commands

    async def get_info(self):
        try:
            return (f"ℹ️ DexSwap v{__version__}\n"
                    f"💱 {await self.get_name()}\n"
                    f"🪪 {self.account_number}")
        except Exception as error:
            return error

    async def get_help(self):
        return (f"{self.commands}\n")


    async def get_name(self):
        if settings.dex_router_contract_addr:
            return str(settings.dex_router_contract_addr)[-8:]

    async def get_account_balance(self):
        account_balance = self.w3.eth.get_balance(
            self.w3.to_checksum_address(self.wallet_address))
        account_balance = self.w3.from_wei(account_balance, 'ether') or 0
        trading_asset_balance = await self.get_trading_asset_balance()
        return f"₿ {round(account_balance,5)}\n💵 {trading_asset_balance}"

    async def get_trading_asset_balance(self):
        trading_asset_balance = await self.contract_utils.get_token_balance(
            self.trading_asset_address, self.wallet_address)
        return trading_asset_balance if trading_asset_balance else 0

    async def get_account_position(self):
        position = "📊 Position\n"
        position += f"Opened: {str(await self.get_account_open_positions())}\n"
        position += f"Margin: {str(await self.get_account_margin())}"
        return position

    async def get_account_margin(self):
        return 0

    async def get_account_open_positions(self):
        return 0

    async def get_account_transactions(self, period=24):
        return await get_account_transactions(
            period,
            self.trading_asset_address,
            self.wallet_address)

    async def get_account_pnl(self, period=24):
        """
        Create a profit and loss (PnL) 
        report for the account.
        """
        pnl_dict = await self.get_account_transactions(period)
        pnl_report = "".join(
            f"{token} {value}\n" for token, value in pnl_dict["tokenList"].items()
        )
        pnl_report += f"Total {pnl_dict['pnl']}\n"
        pnl_report += await self.get_account_position()

        return pnl_report

    async def get_approve(self, token_address):
        """ approve a token """
        try:
            contract = await self.contract_utils.get_token_contract(token_address)
            if contract is None:
                return
            approved_amount = self.w3.to_wei(2 ** 64 - 1, 'ether')
            owner_address = self.w3.to_checksum_address(self.wallet_address)
            dex_router_address = self.w3.to_checksum_address(
                settings.dex_router_contract_addr)
            allowance = contract.functions.allowance(
                owner_address, dex_router_address).call()
            if allowance == 0:
                approval_tx = contract.functions.approve(
                    dex_router_address, approved_amount)
                approval_tx_hash = await self.get_sign(approval_tx.transact())
                return self.w3.eth.wait_for_transaction_receipt(
                    approval_tx_hash)
        except Exception as error:
            raise ValueError(f"Approval failed {error}")

    async def get_sign(self, transaction):
        """ sign a transaction """
        try:
            signed_tx = self.w3.eth.account.sign_transaction(
                transaction, self.private_key)
            return self.w3.eth.send_raw_transaction(
                signed_tx.rawTransaction)
        except Exception as error:
            raise error

    async def get_gas(self, transaction):
        """get gas estimate"""
        gas_limit = self.w3.eth.estimate_gas(transaction) * 1.25
        return int(self.w3.to_wei(gas_limit, 'wei'))

    async def get_gas_price(self):
        """search get gas price"""
        return round(self.w3.from_wei(self.w3.eth.generate_gas_price(), 'gwei'), 2)
