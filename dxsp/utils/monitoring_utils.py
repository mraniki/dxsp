"""
Wallet Monitoring Utilities
"""

import asyncio
from typing import AsyncIterator

from loguru import logger
from web3 import Web3
from web3.types import TxData


class WalletMonitor:
    """
    Monitors a specified wallet address on a given blockchain
    for new transactions using polling and yields them.
    """

    def __init__(self, w3: Web3, address_to_monitor: str, polling_interval: int = 15):
        """
        Initializes the WalletMonitor.

        Args:
            w3 (Web3): The initialized Web3 instance for the target blockchain.
            address_to_monitor (str): The wallet address to monitor.
            polling_interval (int): How often to check for new blocks (in seconds).
        """
        if not w3 or not w3.is_connected():
            logger.error("WalletMonitor requires a connected Web3 instance.")
            raise ValueError("Invalid Web3 instance provided.")

        if not Web3.is_address(address_to_monitor):
            logger.error(
                f"Invalid address provided for monitoring: {address_to_monitor}"
            )
            raise ValueError("Invalid Ethereum address format.")

        self.w3 = w3
        self.address_to_monitor = Web3.to_checksum_address(address_to_monitor)
        self.polling_interval = polling_interval
        self.last_checked_block = -1  # Start from the beginning or latest?
        logger.info(
            f"WalletMonitor initialized for address: {self.address_to_monitor} "
            f"with interval {self.polling_interval}s"
        )

    async def start_monitoring(self) -> AsyncIterator[TxData]:
        """
        Starts monitoring process & yields transactions from the monitored address.
        This runs indefinitely until the consumer stops iterating.
        """
        if self.last_checked_block < 0:
            # Initialize with the block before the current one to avoid missing txns
            # during startup, but don't scan the whole chain on first run.
            try:
                latest_block_num = self.w3.eth.block_number
                self.last_checked_block = max(0, latest_block_num - 1)
                logger.info(
                    f"Monitoring starting from block {self.last_checked_block + 1}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to get initial block number: {e}. Cannot start monitoring."
                )
                return  # Stop the generator if we can't get the initial block

        while True:
            try:
                latest_block_num = self.w3.eth.block_number

                if latest_block_num > self.last_checked_block:
                    logger.debug(
                        f"Checking blocks from {self.last_checked_block + 1} "
                        f"to {latest_block_num}"
                    )
                    for block_num in range(
                        self.last_checked_block + 1, latest_block_num + 1
                    ):
                        try:
                            block = self.w3.eth.get_block(
                                block_num, full_transactions=True
                            )
                            if block and block.transactions:
                                for tx in block.transactions:
                                    # Ensure 'from' exists and matches
                                    # the monitored address
                                    tx_from = tx.get("from")
                                    if (
                                        tx_from
                                        and Web3.to_checksum_address(tx_from)
                                        == self.address_to_monitor
                                    ):
                                        logger.info(
                                            f"Found transaction {tx.hash.hex()} "
                                            f"from {self.address_to_monitor} "
                                            f"in block {block_num}"
                                        )
                                        # Yield the full transaction data object
                                        yield tx
                        except Exception as e:
                            logger.warning(
                                f"Error fetching/processing block {block_num}: {e}"
                            )
                            # Decide if we should retry or skip the block
                            # For now, we'll just log and continue

                    self.last_checked_block = latest_block_num
                else:
                    # No new blocks
                    logger.trace("No new blocks detected.")

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}. Retrying after interval.")
                # Handle specific exceptions? e.g., connection errors

            await asyncio.sleep(self.polling_interval)

    async def stop_monitoring(self):
        """
        Stops the monitoring process.
        """
        logger.info(f"Stopping monitoring for {self.address_to_monitor}.")
        # TODO: Clean up resources (e.g., close WebSocket)

    # Placeholder for callback/event emission when a transaction is found
    async def _on_transaction_found(self, tx_hash):
        logger.info(f"Transaction detected from {self.address_to_monitor}: {tx_hash}")
        # TODO: Implement logic to notify the handler or trigger decoding/copying
