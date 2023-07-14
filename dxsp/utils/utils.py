
import requests
import decimal
from datetime import datetime
from dxsp.config import settings

# ------🛠️ W3 UTILS ---------
async def get(self, url, params=None, headers=None):
    """ gets a url payload """
    try:
        self.logger.debug(f"Requesting URL: {url}")
        response = requests.get(
            url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()

    except Exception as error:
        raise error

async def get_approve(self, token_address):
    """ approve a token """
    try:
        contract = await self.get_token_contract(token_address)
        if contract is None:
            return
        approved_amount = self.w3.to_wei(2 ** 64 - 1, 'ether')
        owner_address = self.w3.to_checksum_address(self.account.wallet_address)
        dex_router_address = self.w3.to_checksum_address(
            settings.dex_router_contract_addr)
        allowance = contract.functions.allowance(
            owner_address, dex_router_address).call()
        if allowance == 0:
            approval_tx = contract.functions.approve(
                dex_router_address, approved_amount)
            approval_tx_hash = await self.get_sign(approval_tx.transact())
            return self.w3.eth.wait_for_transaction_receipt(
                approval_tx_hash)
    except Exception as error:
        raise ValueError(f"Approval failed {error}")

async def get_sign(self, transaction):
    """ sign a transaction """
    try:
        if self.protocol_type == 'uniswap':
            transaction_params = {
                'from': self.account.wallet_address,
                'gas': await get_gas(transaction),
                'gasPrice': await get_gas_price(),
                'nonce': self.w3.eth.get_transaction_count(
                    self.account.wallet_address),
            }
            transaction = transaction.build_transaction(transaction_params)
        signed_tx = self.w3.eth.account.sign_transaction(
            transaction, self.private_key)
        raw_tx_hash = self.w3.eth.send_raw_transaction(
            signed_tx.rawTransaction)
        return self.w3.to_hex(raw_tx_hash)
    except Exception as error:
        raise error


async def calculate_sell_amount(self, sell_token_address, quantity):
    """Returns amount based on risk percentage."""
    sell_balance = await self.get_token_balance(sell_token_address)
    sell_contract = await self.get_token_contract(sell_token_address)
    sell_decimals = (
        sell_contract.functions.decimals().call()
        if sell_contract is not None else 18)
    risk_percentage = settings.trading_risk_amount
    return ((sell_balance / (risk_percentage * 10 ** sell_decimals))
            * (decimal.Decimal(quantity)/ 100)) 


async def get_confirmation(self, transactionHash):
    """Returns trade confirmation."""
    try:
        transaction = self.w3.eth.get_transaction(transactionHash)
        block = self.w3.eth.get_block(transaction["blockNumber"])
        return {
            "timestamp": block["timestamp"],
            "id": transactionHash,
            "instrument": transaction["to"],
            "contract": transaction["to"],   # TBD To be determined.
            "amount": transaction["value"],
            "price": transaction["value"],  # TBD To be determined.
            "fee": transaction["gas"],
            "confirmation": (
                f"➕ Size: {round(transaction['value'], 4)}\n"
                f"⚫️ Entry: {round(transaction['value'], 4)}\n"
                f"ℹ️ {transactionHash}\n"
                f"⛽ {transaction['gas']}\n"
                f"🗓️ {block['timestamp']}"
            ),
        }
    except Exception as error:
        raise error

async def get_gas(self, transaction):
    """get gas estimate"""
    gas_limit = self.w3.eth.estimate_gas(transaction) * 1.25
    return int(self.w3.to_wei(gas_limit, 'wei'))

async def get_gas_price(self):
    """search get gas price"""
    return round(self.w3.from_wei(self.w3.eth.generate_gas_price(), 'gwei'), 2)

async def get_block_timestamp(self, block_num) -> datetime:
        """Get block timestamp"""
        block_info = self.w3.eth.get_block(block_num)
        last_time = block_info["timestamp"]
        return datetime.utcfromtimestamp(last_time)