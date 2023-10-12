class Token:
    def __init__(self, address, name, symbol, decimals, contract):
        self.address = address
        self.name = name
        self.symbol = symbol
        self.decimals = decimals
        self.contract = contract
        # Add more attributes as needed

    def __repr__(self):
        return f"Token(address={self.address}, symbol={self.symbol}, name={self.name}, decimals={self.decimals}, contract={self.contract})"
