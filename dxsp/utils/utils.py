"""
 DEX SWAP
🛠️ W3 UTILS
"""

import requests
from loguru import logger


async def get(url, params=None, headers=None):
    """
    Asynchronously gets a url payload
    and returns the response

    Args:
        url (str): The url to get
        params (dict, optional): The params to send. Defaults to None.
        headers (dict, optional): The headers to send. Defaults to None.

    Returns:
        dict: The response

    Raises:
        Exception: Error

    """
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
        logger.debug(response)
        if response.status_code == 200:
            return response.json()

    except Exception as error:
        logger.error("get: {}", error)

# async def make_request(self, url, headers, params):
#         async with aiohttp.ClientSession(headers=header) as session:
#             async with self.limit, session.get(url=url, params=params) as response:
#                 await asyncio.sleep(self.rate)
#                 resp = await response.read()
#                 return resp