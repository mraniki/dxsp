                                    tx_from = tx.get('from')
                                    if tx_from and Web3.to_checksum_address(tx_from) == self.address_to_monitor:
                                        logger.info(
                                            f"Found transaction {tx.hash.hex()} from "
                                            f"{self.address_to_monitor} in block {block_num}"
                                        )
                                        yield tx # Yield the full transaction data object
                        except Exception as e:
                            logger.warning(
                                f"Error fetching/processing block {block_num}: {e}"
                            )
                            # Decide if we should retry or skip the block
                            # For now, we'll just log and continue 