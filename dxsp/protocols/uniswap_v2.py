"""
uniswap V2  🦄
"""
from dxsp.config import settings


async def get_quote_uniswap_v2(
    cls,
    asset_in_address,
    asset_out_address,
    amount=1
):
    # cls.logger.debug("get_quote_uniswap")
    try:
        router_instance = await cls.router()
        quote = router_instance.functions.getAmountsOut(
            amount,
            [asset_in_address, asset_out_address]).call()
        # cls.logger.error("quote %s", quote)
        if isinstance(quote, list):
            quote = str(quote[0])
        return f"🦄 {quote} {settings.trading_asset}"   
    except Exception as e:
        return e


async def get_approve_uniswap(cls, token_address):
    pass
    # try:
    #     contract = await cls.get_token_contract(token_address)
    #     if contract is None:
    #         return
    #     approved_amount = cls.w3.to_wei(2 ** 64 - 1, 'ether')
    #     owner_address = cls.w3.to_checksum_address(cls.wallet_address)
    #     dex_router_address = cls.w3.to_checksum_address(settings.dex_router_contract_addr)
    #     allowance = contract.functions.allowance(owner_address, dex_router_address).call()
    #     cls.logger.debug("allowance %s", allowance)
    #     if allowance == 0:
    #         approval_tx = contract.functions.approve(dex_router_address, approved_amount)
    #         approval_tx_hash = await cls.get_sign(approval_tx)
    #         return cls.w3.eth.wait_for_transaction_receipt(
    #             approval_tx_hash, timeout=120, poll_latency=0.1
    #         )
    # except Exception as error:
    #     raise ValueError(f"Approval failed {error}") 



async def get_swap_uniswap(cls, asset_out_address, asset_in_address, amount):
    pass
    # try:
    #     path = [cls.w3.to_checksum_address(asset_out_address),
    #             cls.w3.to_checksum_address(asset_in_address)]
    #     deadline = cls.w3.eth.get_block("latest")["timestamp"] + 3600
    #     router_instance = await cls.router()
    #     min_amount = cls.get_quote_uniswap(
    #         asset_in_address, asset_out_address, amount)[0]
    #     return router_instance.functions.swapExactTokensForTokens(
    #         int(amount),
    #         int(min_amount),
    #         tuple(path),
    #         cls.wallet_address,
    #         deadline,
    #     )
    # except Exception as e:
    #     raise ValueError(f"Approval failed {error}") 
