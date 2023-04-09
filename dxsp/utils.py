




import logging
import os
from dotenv import load_dotenv
from pycoingecko import CoinGeckoAPI

#🧐LOGGING
LOGLEVEL=os.getenv("LOGLEVEL", "DEBUG")
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=LOGLEVEL)
logger = logging.getLogger(__name__)
logger.info(msg=f"LOGLEVEL {LOGLEVEL}")


async def search_contract(chain_id,token):
    try:
        token_contract = await get_contract_address(main_list,chain_id,token)
        if token_contract is None:
            token_contract = await get_contract_address(test_token_list,chain_id,token)
            if token_contract is None:
                token_contract = await get_contract_address(personal_list,chain_id,token)
                if token_contract is None:
                    token_contract = await search_gecko_contract(chain_id,token)
        if token_contract:
            return token_contract
    except Exception as e:
        logger.error(msg=f"search_contract error {token} {e}")


#📝tokenlist
main_list = 'https://raw.githubusercontent.com/viaprotocol/tokenlists/main/all_tokens/all.json'
personal_list = os.getenv("TOKENLIST", "https://raw.githubusercontent.com/mraniki/tokenlist/main/TT.json") 
test_token_list=os.getenv("TESTTOKENLIST", "https://raw.githubusercontent.com/mraniki/tokenlist/main/testnet.json")


def get_list(url, params=None, headers=None):
    logger.debug(msg=f"url {url}")
    headers = { "User-Agent": "Mozilla/5.0" }
    response = requests.get(url,params =params,headers=headers)
    logger.debug(msg=f"response {response}")
    logger.debug(msg=f"response json {response.json()}")
    return response.json()

async def get_contract_address(token_list_url, chain_id, symbol):
    try: 
        token_list = get_list(token_list_url)
        logger.debug(msg=f"symbol {symbol}")
        logger.debug(msg=f"chain_id {chain_id}")
        token_search = token_list['tokens']
        for keyval in token_search:
            if (keyval['symbol'] == symbol and keyval['chainId'] == chain_id):
                logger.debug(msg=f"keyval {keyval['address']}")
                return keyval['address']
    except Exception as e:
        logger.debug(msg=f"error {e}")
        return

#🦎GECKO
gecko_api = CoinGeckoAPI() # llama_api = f"https://api.llama.fi/" maybe as backup

async def search_gecko_contract(chain_id,token):
    try:
        coin_info = await search_gecko(chain_id,token)
        coin_contract = coin_info['platforms'][f'{coin_platform}']
        logger.info(msg=f"🦎 contract {token} {coin_contract}")
        return ex.to_checksum_address(coin_contract)
    except Exception:
        return

async def search_gecko(chain_id,token):
    try:
        search_results = gecko_api.search(query=token)
        search_dict = search_results['coins']
        filtered_dict = [x for x in search_dict if x['symbol'] == token.upper()]
        api_dict = [ sub['api_symbol'] for sub in filtered_dict ]
        for i in api_dict:
            coin_dict = gecko_api.get_coin_by_id(i)
            try:
                coin_platform = await search_gecko_platform(chain_id)
                if coin_dict['platforms'][f'{coin_platform}'] is not None:
                    return coin_dict
            except KeyError:
                pass
    except Exception as e:
        logger.error(msg=f"search_gecko error {e}")
        return

async def search_gecko_platform(chain_id):
    try:
        assetplatform = gecko_api.get_asset_platforms()
        output_dict = [x for x in assetplatform if x['chain_identifier'] == int(chain_id)]
        return output_dict[0]['id']
    except Exception as e:
        logger.debug(msg=f"search_gecko_platform error {e}")
