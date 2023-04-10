blockchains = {
    # For pytest mocking
    1000000000000: {
        "url": "https://api.test.io/api?",
        "price": "ethprice",
        "supply": "ethsupply",
        "daily_price": "ethdailyprice",
        "daily_market_cap": "ethdailymarketcap",
    },
    #  ETHEREUM
    1: {
        "url": "https://api.etherscan.io/api?",
        "price": "ethprice",
        "supply": "ethsupply",
        "daily_price": "ethdailyprice",
        "daily_market_cap": "ethdailymarketcap",
    },
    # ETHEREUM Ropsten
    3: {
        "url": "https://api-Ropsten.etherscan.io/api?",
        "price": "ethprice",
        "supply": "ethsupply",
        "daily_price": "ethdailyprice",
        "daily_market_cap": "ethdailymarketcap",
    },
    # ETHEREUM Rinkeby
    4: {
        "url": "https://api-Rinkeby.etherscan.io/api?",
        "price": "ethprice",
        "supply": "ethsupply",
        "daily_price": "ethdailyprice",
        "daily_market_cap": "ethdailymarketcap",
    },
    # ETHEREUM Gorli
    5: {
        "url": "https://api-Goerli.etherscan.io/api?",
        "price": "ethprice",
        "supply": "ethsupply",
        "daily_price": "ethdailyprice",
        "daily_market_cap": "ethdailymarketcap",
    },
    # Ethereum Classic Kotti
    6: {
        "url": "https://blockscout.com/etc/kotti/api?",
        "price": "coinprice",
        "supply": "coinsupply",
        "daily_price": "coindailyprice",  # not available
        "daily_market_cap": "coindailymarketcap",  # not available
    },
    # Optimism
    10: {
        "url": "https://api-optimistic.etherscan.io/api?",
        "price": "optimismprice",  # not available
        "supply": "optimismsupply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # CRONOS
    25: {
        "url": "https://api.cronoscan.com/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # RSK
    30: {
        "url": "https://blockscout.com/rsk/mainnet/api?",
        "price": "coinprice",
        "supply": "coinsupply",
        "daily_price": "coindailyprice",  # not available
        "daily_market_cap": "coindailymarketcap",  # not available
    },
    # ETHEREUM Kovan
    42: {
        "url": "https://api-Kovan.etherscan.io/api?",
        "price": "ethprice",
        "supply": "ethsupply",
        "daily_price": "ethdailyprice",
        "daily_market_cap": "ethdailymarketcap",
    },
    # Binance Smart Chain
    56: {
        "url": "https://api.bscscan.com/api?",
        "price": "bnbprice",
        "supply": "bnbsupply",
        "daily_price": "bnbdailyprice",
        "daily_market_cap": "bnbdailymarketcap",  # not available
    },
    # Ethereum Classic
    61: {
        "url": "https://blockscout.com/etc/mainnet/api?",
        "price": "coinprice",
        "supply": "coinsupply",
        "daily_price": "coindailyprice",  # not available
        "daily_market_cap": "coindailymarketcap",  # not available
    },
    # Ethereum Classic Mordor
    63: {
        "url": "https://blockscout.com/etc/mordor/api?",
        "price": "coinprice",
        "supply": "coinsupply",
        "daily_price": "coindailyprice",  # not available
        "daily_market_cap": "coindailymarketcap",  # not available
    },
    # Optimism kovan
    69: {
        "url": "https://api-kovan-optimistic.etherscan.io/api?",
        "price": "optimismprice",  # not available
        "supply": "optimismsupply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Hoo Smart Chain
    70: {
        "url": "https://hooscan.com/api?",
        "price": "coinprice",
        "supply": "coinsupply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # POA Sokol
    77: {
        "url": "https://blockscout.com/poa/sokol/api?",
        "price": "coinprice",
        "supply": "coinsupply",
        "daily_price": "coindailyprice",  # not available
        "daily_market_cap": "coindailymarketcap",  # not available
    },
    # Binance Smart Chain Testnet
    97: {
        "url": "https://api-testnet.bscscan.com/api?",
        "price": "bnbprice",
        "supply": "bnbsupply",
        "daily_price": "bnbdailyprice",
        "daily_market_cap": "bnbdailymarketcap",  # not available
    },
    # POA Core
    99: {
        "url": "https://blockscout.com/poa/core/api?",
        "price": "coinprice",
        "supply": "coinsupply",
        "daily_price": "coindailyprice",  # not available
        "daily_market_cap": "coindailymarketcap",  # not available
    },
    # Gnosis
    100: {
        "url": "https://blockscout.com/xdai/mainnet/api?",
        "price": "coinprice",
        "supply": "coinsupply",
        "daily_price": "coindailyprice",  # not available
        "daily_market_cap": "coindailymarketcap",  # not available
    },
    # Huobi ECO
    128: {
        "url": "https://api.hecoinfo.com/api?",
        "price": "htprice",
        "supply": "htsupply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Polygon
    137: {
        "url": "https://api.polygonscan.com/api?",
        "price": "maticprice",
        "supply": "maticsupply",
        "daily_price": "ethdailyprice",
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # BitTorrent
    199: {
        "url": "https://api.bttcscan.com/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",
        "daily_market_cap": "ethdailymarketcap",
    },
    # Fantom
    250: {
        "url": "https://api.ftmscan.com/api?",
        "price": "ftmprice",
        "supply": "ftmsupply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Huobi ECO Testnet
    256: {
        "url": "https://api-testnet.hecoinfo.com/api?",
        "price": "htprice",
        "supply": "htsupply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Cronos Testnet
    338: {
        "url": "https://api-testnet.cronoscan.com/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # CLV Parachain
    1024: {
        "url": "https://api.clvscan.com/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # BitTorrent Testnet
    1028: {
        "url": "https://api-testnet.bttcscan.com/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    #  Moonbeam
    1284: {
        "url": "https://api-moonbeam.moonscan.io/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    #  Moonriver
    1285: {
        "url": "https://api-moonriver.moonscan.io/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    #  Moonbase
    1287: {
        "url": "https://api-moonbase.moonscan.io/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Fantom Testnet
    4002: {
        "url": "https://api-testnet.ftmscan.com/api?",
        "price": "ftmprice",
        "supply": "ftmsupply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Arbitrum One
    42161: {
        "url": "https://api.arbiscan.io/api?",
        "price": "price",  # not available
        "supply": "supply",  # not available
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Celo
    42220: {
        "url": "https://api.celoscan.xyz/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    #  Avalanche Fuji Testnet
    43113: {
        "url": "https://api-testnet.snowtrace.io/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Avalanche
    43114: {
        "url": "https://api.snowtrace.io/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Celo Alfajores
    44787: {
        "url": "https://api-alfajores.celoscan.xyz/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Polygon Mumbai
    80001: {
        "url": "https://api-testnet.polygonscan.com/api?",
        "price": "maticprice",
        "supply": "maticsupply",
        "daily_price": "ethdailyprice",
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Artis sigma1
    246529: {
        "url": "https://blockscout.com/artis/sigma1/api?",
        "price": "coinprice",
        "supply": "coinsupply",
        "daily_price": "coindailyprice",  # not available
        "daily_market_cap": "coindailymarketcap",  # not available
    },
    # Arbitrum Rinkeby
    421611: {
        "url": "https://api-testnet.arbiscan.io/api?",
        "price": "price",  # not available
        "supply": "supply",  # not available
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # ETHEREUM Sepolia
    11155111: {
        "url": "https://api-Sepolia.etherscan.io/api?",
        "price": "ethprice",
        "supply": "ethsupply",
        "daily_price": "ethdailyprice",
        "daily_market_cap": "ethdailymarketcap",
    },
    # Aurora
    1313161554: {
        "url": "https://api.aurorascan.dev/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
    # Aurora Testnet
    1313161555: {
        "url": "https://api-testnet.aurorascan.dev/api?",
        "price": "price",  # not available
        "supply": "supply",
        "daily_price": "ethdailyprice",  # not available
        "daily_market_cap": "ethdailymarketcap",  # not available
    },
}