"""
0️⃣x
"""
from dxsp.config import settings
from dxsp.main import DexSwap
import requests

class DexSwapZeroX(DexSwap):

    async def get(url, params=None, headers=None):
        """ gets a url payload """
        try:
            response = requests.get(
                url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()

        except Exception as error:
            raise error

    async def get_quote(self, buy_address, sell_address, amount=1):
        try:
            out_amount = amount * (10 ** await self.contract_utils.get_token_decimals(sell_address))
            url = f"{settings.dex_0x_url}/swap/v1/quote?buyToken={str(buy_address)}&sellToken={str(sell_address)}&sellAmount={str(out_amount)}"
            headers = {"0x-api-key": settings.dex_0x_api_key}
            response = await self.get(url, params=None, headers=headers)
            if response:
                quote = float(response['guaranteedPrice'])
                return quote
        except Exception as error:
            raise ValueError(f"Quote failed {error}") 

    async def get_swap(self, buy_address, sell_address, amount):
        swap_order = await self.get_quote(buy_address, sell_address, amount)
        return await self.account.get_sign(swap_order)