                - follow_wallet (bool): Enable wallet monitoring (default: False).
                - follow_wallet_address (str): Wallet address to monitor.
                - follow_wallet_functions (list[str]): Function names to copy 
                  (default: ["swapExactTokensForTokens"])

        Returns:
            None

        self.follow_wallet = get("follow_wallet", False)
        self.follow_wallet_address = get("follow_wallet_address", None)
        # NEW: Get configurable list of functions to follow
        default_funcs = ["swapExactTokensForTokens"]
        self.follow_wallet_functions = get("follow_wallet_functions", default_funcs)

        self.client = None

        if self.follow_wallet:
            try:
                self.wallet_monitor = WalletMonitor(
                    w3=self.w3,
                    address_to_monitor=self.follow_wallet_address
                )
                logger.info(
                    f"Wallet monitoring activated for "
                    f"{self.follow_wallet_address} on chain {self.chain}"
                )
                self._monitor_task = asyncio.create_task(
                    self._run_monitoring_loop()
                )
                logger.info("Wallet monitoring loop started.")
            except ValueError as e:
                logger.error(f"Error activating wallet monitoring: {e}")

    def _run_monitoring_loop(self):
        # Implementation of _run_monitoring_loop method
        pass 