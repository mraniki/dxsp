"""
uniswap  🦄
"""
from dxsp.config import settings
from dxsp.main import DexSwap
from uniswap import Uniswap



class DexSwapUniswap(DexSwap):
    """
    A DEXSwap sub class using uniswap-python library
    """
    async def get_quote(
        self,
        buy_address,
        sell_address,
        amount=1
    ):
        try:
            uniswap = Uniswap(
                address=self.wallet_address,
                private_key=self.private_key,
                version=self.protocol_version, web3=self.w3,
                factory_contract_addr=settings.dex_factory_contract_addr,
                router_contract_addr=settings.dex_router_contract_addr
                )
            amount_wei = amount * (10 ** (
                await self.get_token_decimals(sell_address)))
            quote = uniswap.get_price_input(
                sell_address, buy_address, amount_wei)
            return round(
                float((quote /
                       (10 **
                        (await self.get_token_decimals(buy_address))))), 5)

        except Exception as error:
            raise ValueError(f"Quote failed {error}") 

    async def get_swap(self, sell_address, buy_address, amount):
        try:
            uniswap = Uniswap(
                        address=self.wallet_address,
                        private_key=self.private_key,
                        version=2, web3=self.w3,
                        factory_contract_addr=settings.dex_factory_contract_addr,
                        router_contract_addr=settings.dex_router_contract_addr
                        )
            return uniswap.make_trade(
                sell_address, buy_address, amount)

        except Exception as error:
            raise ValueError(f"Swap failed {error}") 
