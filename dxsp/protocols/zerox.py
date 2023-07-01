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


    async def get_swap(self, buy_address, sell_address, amount):
        swap_order = await self.get_quote(buy_address, sell_address, amount)
        return await self.get_sign(swap_order)