
# to be used https://github.com/ethereum-lists/chains/tree/master/_data/chains

#https://raw.githubusercontent.com/ethereum-lists/chains/master/_data/chains/eip155-10.json
#https://chainid.network/chains.json


blockchains = {
    #  ETHEREUM
    1: {
        "block_explorer_url": "https://api.etherscan.io/api?",
        "rpc": "https://rpc.ankr.com/eth",
        "uniswap_v2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "uniswap_v3": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "1inch": "https://api.1inch.exchange/v5.0/1",
        "1inch_limit": "https://limit-orders.1inch.io/v3.0/1",
        "0x": "https://api.0x.org/"
    },
    # ETHEREUM Gorli
    5: {
        "block_explorer_url": "https://api-Goerli.etherscan.io/api?",
        "rpc": "https://rpc.ankr.com/eth_goerli",
        "uniswap_v2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "uniswap_v3": "",
        "1inch": "",
        "1inch_limit": "",
        "0x": "https://goerli.api.0x.org/"
    },
    # ETHEREUM Sepolia
    11155111: {
        "block_explorer_url": "https://api-Sepolia.etherscan.io/api?",
        "rpc": "https://rpc.ankr.com/eth_sepolia",
        "uniswap_v2": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "uniswap_v3": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "1inch": "",
        "1inch_limit": "",
        "0x": "https://sepolia.api.0x.org/"
        },
    # Binance Smart Chain
    56: {
        "block_explorer_url": "https://api.bscscan.com/api?",
        "rpc": "https://rpc.ankr.com/bsc",
        "uniswap_v2": "0xca143ce32fe78f1f7019d7d551a6402fc5350c73", #pancakeswap
        "uniswap_v3": "",
        "1inch": "https://api.1inch.exchange/v5.0/56",
        "1inch_limit": "https://limit-orders.1inch.io/v3.0/56",
        "0x": "https://bsc.api.0x.org/"
        },
    # Binance Smart Chain Testnet
    97: {
        "block_explorer_url": "https://api-testnet.bscscan.com/api?",
        "rpc": "https://rpc.ankr.com/bsc_testnet_chapel",
        "uniswap_v2": "",
        "uniswap_v3": "",
        "1inch": "",
        "1inch_limit": "",
        "0x": ""
        },
    # Arbitrum One
    42161: {
        "block_explorer_url": "https://api.arbiscan.io/api?",
        "rpc": "https://rpc.ankr.com/arbitrum",
        "uniswap_v2": "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f",
        "uniswap_v3": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "1inch": "https://api.1inch.exchange/v5.0/42161",
        "1inch_limit": "https://limit-orders.1inch.io/v3.0/42161",
        "0x": "https://arbitrum.api.0x.org/"
        },
    # Arbitrum Rinkeby
    421611: {
        "block_explorer_url": "https://api-testnet.arbiscan.io/api?",
        "rpc": "https://rinkeby.arbitrum.io/rpc",
        "uniswap_v2": "",
        "uniswap_v3": "",
        "1inch": "",
        "1inch_limit": "",
        "0x": ""
        },
    # Polygon
    137: {
        "block_explorer_url": "https://api.polygonscan.com/api?",
        "rpc": "https://rpc.ankr.com/polygon",
        "uniswap_v2": "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f",
        "uniswap_v3": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "1inch": "https://api.1inch.exchange/v5.0/137",
        "1inch_limit": "https://api.1inch.exchange/v5.0/137",
        "0x": "https://polygon.api.0x.org/"
    },
    # Polygon Mumbai
    80001: {
        "block_explorer_url": "https://api-testnet.polygonscan.com/api?",
        "rpc": "https://rpc.ankr.com/polygon_mumbai",
        "uniswap_v2": "",
        "uniswap_v3": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "1inch": "",
        "1inch_limit": "",
        "0x": "https://mumbai.api.0x.org/"
        },
    # Polygon zkEVM
    1101: {
        "block_explorer_url": "",
        "rpc": "https://rpc.ankr.com/polygon_zkevm",
        "uniswap_v2": "",
        "uniswap_v3": "",
        "1inch": "",
        "1inch_limit": "h",
        "0x": ""
    },
    # Polygon zkEVM testnet
    1442: {
        "block_explorer_url": "",
        "rpc": "https://rpc.ankr.com/polygon_zkevm_testnet",
        "uniswap_v2": "",
        "uniswap_v3": "",
        "1inch": "",
        "1inch_limit": "h",
        "0x": ""
    },
    # Optimism
    10: {
        "block_explorer_url": "https://api-optimistic.etherscan.io/api?",
        "rpc": "https://rpc.ankr.com/optimism",
        "uniswap_v2": "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f",
        "uniswap_v3": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "1inch": "https://api.1inch.exchange/v5.0/10",
        "1inch_limit": "https://limit-orders.1inch.io/v3.0/10",
        "0x": "https://optimism.api.0x.org/"
    },
    # Optimism goerli
    69: {
        "block_explorer_url": "https://api-Goerli.etherscan.io/api? ne",
        "rpc": "https://rpc.ankr.com/optimism_testnet",
        "uniswap_v2": "",
        "uniswap_v3": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "1inch": "",
        "1inch_limit": "",
        "0x": ""
        },
    # Avalanche
    43114: {
        "block_explorer_url": "https://api.snowtrace.io/api?",
        "rpc": "https://rpc.ankr.com/avalanche",
        "uniswap_v2": "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f",
        "uniswap_v3": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "1inch": "https://api.1inch.exchange/v5.0/43114",
        "1inch_limit": "https://limit-orders.1inch.io/v3.0/43114",
        "0x": "https://avalanche.api.0x.org/"
        },
    #  Avalanche Fuji Testnet
    43113: {
        "block_explorer_url": "https://api-testnet.snowtrace.io/api?",
        "rpc": "https://rpc.ankr.com/avalanche_fuji",
        "uniswap_v2": "",
        "uniswap_v3": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "1inch": "",
        "1inch_limit": "",
        "0x": ""
        },
    # Fantom
    250: {
        "block_explorer_url": "https://api.ftmscan.com/api?",
        "rpc": "https://rpc.ankr.com/fantom",
        "uniswap_v2": "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f",
        "uniswap_v3": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "1inch": "https://api.1inch.exchange/v5.0/250",
        "1inch_limit": "https://limit-orders.1inch.io/v3.0/250",
        "0x": "https://fantom.api.0x.org/"
        },
    # Fantom Testnet
    4002: {
        "block_explorer_url": "https://api-testnet.ftmscan.com/api?",
        "rpc": "https://rpc.ankr.com/fantom_testnet",
        "uniswap_v2": "",
        "uniswap_v3": "0x1f98431c8ad98523631ae4a59f267346ea31f984",
        "1inch": "",
        "1inch_limit": "",
        "0x": ""
        },
    # Celo
    42220: {
        "block_explorer_url": "http://explorer.celo.org/api?",
        "rpc": "https://rpc.ankr.com/celo",
        "uniswap_v2": "",
        "uniswap_v3": "0xAfE208a311B21f13EF87E33A90049fC17A7acDEc",
        "1inch": "",
        "1inch_limit": "",
        "0x": "https://celo.api.0x.org/"
        },
    # Celo Alfajores Testnet
    44787: {
        "block_explorer_url": "https://alfajores-blockscout.celo-testnet.org/api?",
        "rpc": "https://alfajores-forno.celo-testnet.org",
        "uniswap_v2": "",
        "uniswap_v3": "0xAfE208a311B21f13EF87E33A90049fC17A7acDEc",
        "1inch": "",
        "1inch_limit": "",
        "0x": ""
        },
    # Gnosis
    100: {
        "block_explorer_url": "https://api.gnosisscan.io.com/api?",
        "rpc": "https://rpc.ankr.com/gnosis",
        "uniswap_v2": "",
        "uniswap_v3": "",
        "1inch": "https://api.1inch.exchange/v5.0/100",
        "1inch_limit": "https://limit-orders.1inch.io/v3.0/250",
        "0x": "https://fantom.api.0x.org/"
        },
    # Klaytn
    8217: {
        "block_explorer_url": "https://scope.klaytn.com",
        "rpc": "https://rpc.ankr.com/klaytn",
        "uniswap_v2": "",
        "uniswap_v3": "",
        "1inch": "https://api.1inch.exchange/v5.0/8217",
        "1inch_limit": "https://limit-orders.1inch.io/v3.0/8217",
        "0x": ""
        },
    # Klaytn testnet
    1001: {
        "block_explorer_url": "",
        "rpc": "https://rpc.ankr.com/klaytn_testnet",
        "uniswap_v2": "",
        "uniswap_v3": "",
        "1inch": "",
        "1inch_limit": "",
        "0x": ""
        },
    # Aurora
    1313161554: {
        "block_explorer_url": "https://explorer.aurora.dev/api/",
        "rpc": "https://mainnet.aurora.dev",
        "uniswap_v2": "0x2CB45Edb4517d5947aFdE3BEAbF95A582506858B", #trisolaris
        "uniswap_v3": "0x2CB45Edb4517d5947aFdE3BEAbF95A582506858B", #trisolaris
        "1inch": "https://api.1inch.exchange/v5.0/1313161554",
        "1inch_limit": "https://limit-orders.1inch.io/v3.0/1313161554",
        "0x": "h"
        },
    # Aurora
    1313161555: {
        "block_explorer_url": "https://explorer.testnet.aurora.dev/api/",
        "rpc": "https://testnet.aurora.dev",
        "uniswap_v2": "",
        "uniswap_v3": "",
        "1inch": "",
        "1inch_limit": "",
        "0x": ""
        },
}