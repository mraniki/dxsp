"""
Base DexClient Class   🦄
"""



from typing import Optional

from web3 import Web3


class DexClient:
    def __init__(
        self,
        w3: Optional[Web3] = None,
        protocol_type="uniswap",
        protocol_version=2,
        api_endpoint="https://api.0x.org/",
        api_key=None,
        router=None,
        trading_asset_address=None,
        block_explorer_url="https://api.etherscan.io/api?",
        block_explorer_api=None
    ):
        self.protocol_type = protocol_type
        
        if self.protocol_type == "0x":
            from dxsp.protocols.zerox import DexZeroX
            self.dex_swap = DexZeroX()
        elif self.protocol_type == "1inch":
            from dxsp.protocols.oneinch import DexOneInch
            self.dex_swap = DexOneInch()
        else:
            from dxsp.protocols.uniswap import DexUniswap
            self.dex_swap = DexUniswap()


    async def get_quote(self, buy_address, sell_address, amount=1):
        """

        """
        pass

    async def get_swap(self, sell_address, buy_address, amount):
        """
        """
        pass
