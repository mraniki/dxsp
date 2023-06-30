"""
uniswap V2  🦄
"""
from dxsp.config import settings
from dxsp.main import DexSwap

class DexSwapUniswapV2(DexSwap):
    async def get_quote(
        self,
        asset_in_address,
        asset_out_address,
        amount=1
    ):
       
        # self.logger.debug("get_quote_uniswap")
        try:
            router_instance = await self.router()
            quote = router_instance.functions.getAmountsOut(
                amount,
                [asset_in_address, asset_out_address]).call()
            # self.logger.error("quote %s", quote)
            if isinstance(quote, list):
                quote = str(quote[0])
            return f"🦄 {quote} {settings.trading_asset}"   
        except Exception as error:
            raise ValueError(f"Quote failed {error}") 


    async def get_approve(self, token_address):
        # pass
        try:
            contract = await self.get_token_contract(token_address)
            if contract is None:
                return
            approved_amount = self.w3.to_wei(2 ** 64 - 1, 'ether')
            owner_address = self.w3.to_checksum_address(self.wallet_address)
            dex_router_address = self.w3.to_checksum_address(settings.dex_router_contract_addr)
            allowance = contract.functions.allowance(owner_address, dex_router_address).call()
            # self.logger.debug("allowance %s", allowance)
            if allowance == 0:
                approval_tx = contract.functions.approve(dex_router_address, approved_amount)
                approval_tx_hash = await self.get_sign(approval_tx)
                return self.w3.eth.wait_for_transaction_receipt(
                    approval_tx_hash, timeout=120, poll_latency=0.1
                )
        except Exception as error:
            raise ValueError(f"Approval failed {error}") 



    async def get_swap(self, asset_out_address, asset_in_address, amount):
        # pass
        try:
            path = [self.w3.to_checksum_address(asset_out_address),
                    self.w3.to_checksum_address(asset_in_address)]
            deadline = self.w3.eth.get_block("latest")["timestamp"] + 3600
            router_instance = await self.router()
            min_amount = self.get_quote(
                asset_in_address, asset_out_address, amount)[0]
            return router_instance.functions.swapExactTokensForTokens(
                int(amount),
                int(min_amount),
                tuple(path),
                self.wallet_address,
                deadline,
            )
        except Exception as error:
            raise ValueError(f"Swap failed {error}") 
