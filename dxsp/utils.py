




import logging
import os
from dotenv import load_dotenv
from pycoingecko import CoinGeckoAPI

#🧐LOGGING
LOGLEVEL=os.getenv("LOGLEVEL", "INFO")
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=LOGLEVEL)
logger = logging.getLogger(__name__)
logger.info(msg=f"LOGLEVEL {LOGLEVEL}")

#🔗API
gecko_api = CoinGeckoAPI() # llama_api = f"https://api.llama.fi/" maybe as backup

#📝tokenlist
main_list = 'https://raw.githubusercontent.com/viaprotocol/tokenlists/main/all_tokens/all.json'
personal_list = os.getenv("TOKENLIST", "https://raw.githubusercontent.com/mraniki/tokenlist/main/TT.json") 
test_token_list=os.getenv("TESTTOKENLIST", "https://raw.githubusercontent.com/mraniki/tokenlist/main/testnet.json")


async def search_contract(token):
    try:
        token_contract = await search_json_contract(main_list,token)
        if token_contract is None:
            token_contract = await get_contract_address(test_token_list,token)
            if token_contract is None:
                token_contract = await search_json_contract(personal_list,token)
                if token_contract is None:
                    token_contract = await search_gecko_contract(token)
        if token_contract:
            return ex.to_checksum_address(token_contract)
    except Exception as e:
        logger.error(msg=f"search_contract error {token} {e}")

def get(url, params=None, headers=None):
    logger.debug(msg=f"url {url}")
    headers = { "User-Agent": "Mozilla/5.0" }
    response = requests.get(url,params =params,headers=headers)
    logger.debug(msg=f"response {response}")
    #logger.debug(msg=f"response json {response.json()}")
    return response.json()

#🦎GECKO
async def search_gecko_contract(token):
    try:
        coin_info = await search_gecko(token)
        coin_contract = coin_info['platforms'][f'{coin_platform}']
        logger.info(msg=f"🦎 contract {token} {coin_contract}")
        return ex.to_checksum_address(coin_contract)
    except Exception:
        return

async def search_gecko(token):
    try:
        search_results = gecko_api.search(query=token)
        search_dict = search_results['coins']
        filtered_dict = [x for x in search_dict if x['symbol'] == token.upper()]
        api_dict = [ sub['api_symbol'] for sub in filtered_dict ]
        for i in api_dict:
            coin_dict = gecko_api.get_coin_by_id(i)
            try:
                if coin_dict['platforms'][f'{coin_platform}'] is not None:
                    return coin_dict
            except KeyError:
                pass
    except Exception as e:
        logger.error(msg=f"search_gecko error {e}")
        return

async def get_contract_address(token_list_url, symbol):
    try: 
        token_list = get(token_list_url)
        logger.debug(msg=f"symbol {symbol}")
        logger.debug(msg=f"self.chain_id {self.chain_id}")
        token_search = token_list['tokens']
        for keyval in token_search:
            if (keyval['symbol'] == symbol and keyval['chainId'] == self.chain_id):
                logger.debug(msg=f"keyval {keyval['address']}")
                return keyval['address']
    except Exception as e:
        logger.debug(msg=f"error {e}")
        return