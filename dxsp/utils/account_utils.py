"""
 DEX SWAP
🔒 USER RELATED
"""
import logging
from typing import Optional
from web3 import Web3
from datetime import datetime, timedelta
from dxsp.config import settings
from dxsp import __version__


class AccountUtils:

    def __init__(self, w3: Optional[Web3] = None):
        self.logger = logging.getLogger(name="DexSwap")
        self.w3 = w3 or Web3(Web3.HTTPProvider(settings.dex_rpc))
        self.wallet_address = self.w3.to_checksum_address(
            settings.dex_wallet_address)
        self.account = (f"{str(self.w3.net.version)} - "
                        f"{str(self.wallet_address[-8:])}")
        self.private_key = settings.dex_private_key
        self.trading_asset_address = self.w3.to_checksum_address(
        settings.trading_asset_address)

    async def get_info(self):
        return (f"ℹ️ {__class__.__name__} {__version__}\n"
                f"💱 {await self.get_name()}\n"
                f"🪪 {self.account}")

    async def get_name(self):
        if settings.dex_router_contract_addr:
            return settings.dex_router_contract_addr[-8:]
        else:
            return self.protocol_type

    async def get_account_balance(self):
        account_balance = self.w3.eth.get_balance(
            self.w3.to_checksum_address(self.wallet_address))
        account_balance = self.w3.from_wei(account_balance, 'ether') or 0
        trading_asset_balance = await self.get_trading_asset_balance()
        return f"₿ {round(account_balance,5)}\n💵 {trading_asset_balance}"

    async def get_trading_asset_balance(self):
        trading_asset_balance = await self.get_token_balance(
            self.trading_asset_address)
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

    async def get_account_transactions(self, period=24):
        """
        Retrieves the account transactions 
        within a specified time period
        for the main asset activity
        """
        pnl_dict = {"pnl": 0, "tokenList": {}}
        if not settings.dex_block_explorer_api:
            return pnl_dict
    
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": self.trading_asset_address,
            "address": self.wallet_address,
            "page": "1",
            "offset": "100",
            "startblock": "0",
            "endblock": "99999999",
            "sort": "desc",
            "apikey": settings.dex_block_explorer_api
        }
    
        response = await self.get(
            url=settings.dex_block_explorer_url, params=params)
    
        if response.get('status') == "1" and "result" in response:
            current_time = datetime.utcnow()
            time_history_start = current_time - timedelta(hours=period)
    
            for entry in response["result"]:
                token_symbol = entry.get("tokenSymbol")
                value = int(entry.get("value", 0))
                timestamp = int(entry.get("timeStamp", 0))
                transaction_time = datetime.utcfromtimestamp(timestamp)
    
                if transaction_time >= time_history_start and token_symbol:
                    pnl_dict["tokenList"][token_symbol] = (
                    pnl_dict["tokenList"].get(token_symbol, 0) + value)
                    pnl_dict["pnl"] += value
    
        return pnl_dict
        