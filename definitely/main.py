import json
import requests
from web3 import Web3
import many_abis as ma

class UnknownToken(Exception):
    pass

class DexSwap:
    base_url = 'https://api.1inch.exchange'

    version = {
        "v5.0": "v5.0"
    }

    def __init__(self, address, chain=, version='v5.0'):
        self.presets = None
        self.tokens = {}
        self.tokens_by_address = {}
        self.protocols = []
        self.address = address
        self.version = version
        self.chain_id = self.chains[chain]
        self.chain = chain
        self.tokens = self.get_tokens()
        self.spender = self.get_spender()

    @staticmethod
    def _get(url, params=None, headers=None):
        """ Implements a get request """
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
        except requests.exceptions.ConnectionError as e:
            print("ConnectionError when doing a GET request from {}".format(url))
            payload = None
        except requests.exceptions.HTTPError:
            print("HTTPError {}".format(url))
            payload = None
        return payload


    def get_swap(self, from_token_symbol: str, to_token_symbol: str,
                 amount: float, slippage: float, decimal=None, send_address=None, **kwargs):
        """
        Calls the SWAP API endpoint. NOTE: When using custom tokens, the token decimal is assumed to be 18. If your
        custom token has a different decimal - please manually pass it to the function (decimal=x)
        """
        if send_address is None:
            send_address = self.address
        else:
            pass
        from_address = self._token_to_address(from_token_symbol)
        to_address = self._token_to_address(to_token_symbol)
        if decimal is None:
            try:
                self.tokens[from_token_symbol]['decimals']
            except KeyError:
                decimal = 18
            else:
                decimal = self.tokens[from_token_symbol]['decimals']
        else:
            pass
        if decimal == 0:
            amount_in_wei = int(amount)
        else:
            amount_in_wei = int(amount * 10 ** decimal)
        url = f'{self.base_url}/{self.version}/{self.chain_id}/swap'
        url = url + f'?fromTokenAddress={from_address}&toTokenAddress={to_address}&amount={amount_in_wei}'
        url = url + f'&fromAddress={send_address}&slippage={slippage}'
        if kwargs is not None:
            result = self._get(url, params=kwargs)
        else:
            result = self._get(url)
        return result


    def get_approve(self, from_token_symbol: str, amount=None, decimal=None):
        from_address = self._token_to_address(from_token_symbol)
        if decimal is None:
            try:
                self.tokens[from_token_symbol]['decimals']
            except KeyError:
                decimal = 18
            else:
                decimal = self.tokens[from_token_symbol]['decimals']
        else:
            pass
        url = f'{self.base_url}/{self.version}/{self.chain_id}/approve/transaction'
        if amount is None:
            url = url + f"?tokenAddress={from_address}"
        else:
            if decimal == 0:
                amount_in_wei = int(amount)
            else:
                amount_in_wei = int(amount * 10 ** decimal)
            url = url + f"?tokenAddress={from_address}&amount={amount_in_wei}"
        result = self._get(url)
        return result

if __name__ == '__main__':
    pass