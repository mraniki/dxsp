class FinancialInstrument:
    def __init__(self, name, symbol, address, alt_symbol=None):
        self.name = name
        self.symbol = symbol
        self.address = address
        self.alt_symbol = alt_symbol

    def __str__(self):
        return f"{self.name} ({self.symbol})"
