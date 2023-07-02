"""
uniswap  🦄
"""
from dxsp.config import settings
from dxsp.main import DexSwap
from uniswap import Uniswap



class DexSwapUniswap(DexSwap):
    async def get_quote(
        self,
        buy_address,
        sell_address,
        amount=10
    ):
        try:
            uniswap = Uniswap(address=self.wallet_address, private_key=self.private_key, version=2, web3=self.w3, router_contract_addr=settings.dex_router_contract_addr)
            uniswap.get_price_input(sell_address, buy_address, amount ** await self.get_token_decimals(buy_address))
            # await self.router_contract()
            # if self.protocol_type == "uniswap_v2":
            #     await self.router_contract()
            #     path = [sell_address,buy_address]
            #     print(path)
            #     amount_out = self.router.functions.getAmountsOut(
            #         amount * await self.get_token_decimals(buy_address),
            #         path).call()[-1]
            #     quote = int(amount_out / await self.get_token_decimals(sell_address))
            #     return quote

            # if self.protocol_type == "uniswap_v3":
            #     pass
                # await self.quoter_contract()
                # sqrtPriceLimitX96 = 0
                # fee = 3000
                # quote = self.quoter.functions.quoteExactInputSingle(
                #     buy_address,
                #     sell_address,
                #     fee, amount, sqrtPriceLimitX96).call()
                # return quote

        except Exception as error:
            raise ValueError(f"Quote failed {error}") 


    async def get_swap(self, sell_address, buy_address, amount):
        try:
            await self.router_contract()
            if self.protocol_type == "uniswap_v2":
                path = [self.w3.to_checksum_address(sell_address),
                        self.w3.to_checksum_address(buy_address)]
                deadline = self.w3.eth.get_block("latest")["timestamp"] + 3600
                await self.router_contract()
                min_amount = await self.get_quote(
                    buy_address, sell_address, amount)
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
