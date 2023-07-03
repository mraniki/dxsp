"""
uniswap  🦄
"""
from dxsp.config import settings
from dxsp.main import DexSwap
from uniswap import Uniswap



class DexSwapUniswap(DexSwap):
    """
    A class to demonstrate the use of the Uniswap V2 pool with the
    DEXSwap class.
    """
    # def get_uniswap():
    #     uniswap = Uniswap(
    #     address=self.wallet_address,
    #     private_key=self.private_key,
    #     version=2, web3=self.w3,
    #     factory_contract_addr=settings.dex_factory_contract_addr,
    #     router_contract_addr=settings.dex_router_contract_addr
    #     )
    #     return uniswap
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
            version=2, web3=self.w3,
            factory_contract_addr=settings.dex_factory_contract_addr,
            router_contract_addr=settings.dex_router_contract_addr
            )
            amount_wei = amount * (10 ** (
                await self.get_token_decimals(sell_address)))
            quote = uniswap.get_price_input(
                sell_address, buy_address, amount_wei)
            quote = round(
                float((quote / 
                       (10 ** 
                        (await self.get_token_decimals(buy_address))))), 5)
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
            return quote

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
            swap = uniswap.make_trade(
                sell_address, buy_address, amount)
            return swap
            # #swap = round(
            #     float((quote / 
            #            (10 ** 
            #             (await self.get_token_decimals(buy_address))))), 5)
            # await self.router_contract()
            # if self.protocol_type == "uniswap_v2":
            #     path = [self.w3.to_checksum_address(sell_address),
            #             self.w3.to_checksum_address(buy_address)]
            #     deadline = self.w3.eth.get_block("latest")["timestamp"] + 3600
            #     await self.router_contract()
            #     min_amount = await self.get_quote(
            #         buy_address, sell_address, amount)
            #     return self.router.functions.swapExactTokensForTokens(
            #         int(min_amount),
            #         int(min_amount),
            #         tuple(path),
            #         self.wallet_address,
            #         deadline,
            #     )

        except Exception as error:
            raise ValueError(f"Swap failed {error}") 
