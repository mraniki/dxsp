"""
uniswap V3  🦄
"""

from dxsp.config import settings
from dxsp.main import DexSwap

class DexSwapUniswapV3(DexSwap):


    # async def quoter(self):
    #     try:
    #         quoter_abi = await self.get_abi(settings.dex_quoter_contract_addr)
    #         if quoter_abi is None:
    #             quoter_abi = await self.get(settings.dex_quoter_abi_url)
    #         contract = self.w3.eth.contract(
    #             address=self.w3.to_checksum_address(
    #                 settings.dex_quoter_contract_addr),
    #             abi=quoter_abi)
    #         return contract
    #     except Exception as error:
    #         raise error

    async def get_quote(
        self,
        asset_in_address,
        asset_out_address,
        amount=1
    ):
        pass
        # try:
        #     quoter = await self.quoter()
        #     sqrtPriceLimitX96 = 0
        #     fee = 3000
        #     quote = quoter.functions.quoteExactInputSingle(
        #         asset_in_address,
        #         asset_out_address,
        #         fee, amount, sqrtPriceLimitX96).call()
        #     return f"🦄 {quote} {settings.trading_asset}"
        # except Exception as e:
        #     return e


    # async def get_swap(self, asset_out_address, asset_in_address, amount):
    #     pass