"""
0️⃣x
"""
from dxsp.config import settings
from dxsp.main import DexSwap

class DexSwapZeroX(DexSwap):
    async def get_quote(self, buy_address, sell_address, amount=1):
        #pass
        try:
            out_amount = self.w3.to_wei(amount, 'ether')
            url = f"{settings.dex_0x_url}/swap/v1/quote?buyToken={str(buy_address)}&sellToken={str(sell_address)}&buyAmount={str(out_amount)}"
            headers = {"0x-api-key": settings.dex_0x_api_key}
            response = await self.get(url, params=None, headers=headers)
            print(response)
            if response:
                return round(float(response['guaranteedPrice']), 3)
        except Exception as error:
            raise ValueError(f"Quote failed {error}") 

    async def get_approve(self, token_address):
        try:
            contract = await self.get_token_contract(token_address)
            if contract is None:
                return
            approved_amount = self.w3.to_wei(2 ** 64 - 1, 'ether')
            owner_address = self.w3.to_checksum_address(self.wallet_address)
            dex_router_address = self.w3.to_checksum_address(settings.dex_router_contract_addr)
            allowance = contract.functions.allowance(owner_address, dex_router_address).call()
            if allowance == 0:
                approval_tx = contract.functions.approve(dex_router_address, approved_amount)
                approval_tx_hash = await self.get_sign(approval_tx)
                return self.w3.eth.wait_for_transaction_receipt(
                    approval_tx_hash, timeout=120, poll_latency=0.1
                )
        except Exception as error:
            raise ValueError(f"Approval failed {error}") 

    async def get_swap(self, buy_address, sell_address, amount):
        swap_order = await self.get_quote(buy_address, sell_address, amount)
        return await self.get_sign(swap_order)