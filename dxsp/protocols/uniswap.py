"""
uniswap V2  🦄
"""
from dxsp.config import settings
from dxsp.main import DexSwap

class DexSwapUniswap(DexSwap):


    async def get_quote(
        self,
        asset_in_address,
        asset_out_address,
        amount=1
    ):
        try:
            await self.router_contract()
            if self.protocol_type == "uniswap_v2":
                await self.router_contract()
                quote = self.router.functions.getAmountsOut(
                    amount,
                    [asset_in_address, asset_out_address]).call()
                self.logger.error("quote %s", quote)
                if isinstance(quote, list):
                    quote = str(quote[0])
                return quote

            if self.protocol_type == "uniswap_v3":
                pass
                # await self.quoter_contract()
                # sqrtPriceLimitX96 = 0
                # fee = 3000
                # quote = self.quoter.functions.quoteExactInputSingle(
                #     asset_in_address,
                #     asset_out_address,
                #     fee, amount, sqrtPriceLimitX96).call()
                # return quote

        except Exception as error:
            raise ValueError(f"Quote failed {error}") 


    async def get_swap(self, asset_out_address, asset_in_address, amount):
        try:
            await self.router_contract()
            if self.protocol_type == "uniswap_v2":
                path = [self.w3.to_checksum_address(asset_out_address),
                        self.w3.to_checksum_address(asset_in_address)]
                deadline = self.w3.eth.get_block("latest")["timestamp"] + 3600
                await self.router_contract()
                min_amount = await self.get_quote(
                    asset_in_address, asset_out_address, amount)
                return self.router.functions.swapExactTokensForTokens(
                    int(amount),
                    int(min_amount),
                    tuple(path),
                    self.wallet_address,
                    deadline,
                )
            if self.protocol_type == "uniswap_v3":
                return
        except Exception as error:
            raise ValueError(f"Swap failed {error}") 
