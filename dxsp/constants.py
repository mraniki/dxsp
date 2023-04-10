from dataclasses import dataclass

@dataclass(frozen=True)
class CHAIN_CONTRACT_API:
    1: str = 'https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    56: str = 'https://api.bscscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    HECO: str = 'https://api.hecoinfo.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    MATIC: str = 'https://api.polygonscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    FTM: str = 'https://api.ftmscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    MOONRIVER: str = 'https://api-moonriver.moonscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    # showtrace
    AVAX: str = 'https://api.snowtrace.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    ARBITRUM: str = 'https://api.arbiscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    CRONOS: str = 'https://api.cronoscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'
    10: str = 'https://api-optimistic.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}'