"""
uniswap  🦄
"""
# from eth_defi.abi import get_contract
from loguru import logger

from dxsp.protocols import DexClient

# from eth_defi.chain import install_chain_middleware, install_retry_middleware,
# install_api_call_counter_middleware
# from eth_defi.event_reader.block_time import measure_block_time
# from eth_defi.event_reader.conversion import decode_data, convert_int256_bytes_to_int,
# convert_jsonrpc_value_to_int
# from eth_defi.event_reader.csv_block_data_store import CSVDatasetBlockDataStore
# from eth_defi.event_reader.fast_json_rpc import patch_web3
# from eth_defi.event_reader.reader import read_events, LogResult, prepare_filter
# from eth_defi.event_reader.reorganisation_monitor import ChainReorganisationDetected,
# JSONRPCReorganisationMonitor
# from eth_defi.uniswap_v2.pair import PairDetails, fetch_pair_details


class DexEvm(DexClient):
    """
    A DexClient using Web3-Ethereum-Defi Python package
    More info:
    https://web3-ethereum-defi.readthedocs.io/index.html

    """

    async def get_quote(self, buy_address=None, symbol=None, amount=1):
        logger.debug("Evm get_quote {} {} {}", buy_address, symbol, amount)
        # dex = fetch_deployment(
        #     self.w3,
        #     factory_address=self.factory_contract_addr,
        #     router_address=self.router_contract_addr,
        # )

    async def make_swap(self, sell_address, buy_address, amount):
        logger.debug("Evm make_swap {} {} {}", sell_address, buy_address, amount)
