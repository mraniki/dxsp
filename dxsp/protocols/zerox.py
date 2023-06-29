"""
0️⃣x
"""


@classmethod
async def get_zerox_quote(cls, buy_address, sell_address, amount=1):
    try:
        out_amount = cls.w3.to_wei(amount, 'ether')
        url = f"{settings.dex_0x_url}/swap/v1/quote?buyToken={str(buy_address)}&sellToken={str(sell_address)}&buyAmount={str(out_amount)}"
        headers = {"0x-api-key": settings.dex_0x_api_key}
        response = await self.get(url, params=None, headers=headers)
        print(response)
        if response:
            return round(float(response['guaranteedPrice']), 3)
    except Exception as e:
        raise e
