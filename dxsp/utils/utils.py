"""
 DEX SWAP
🛠️ W3 UTILS
"""

import requests
import aiohttp
from loguru import logger

MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # Maximum response size in bytes (e.g., 5 MB)

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
    
    # try:
    #     response = requests.get(url, params=params, headers=headers, timeout=20)
    #     logger.debug(response)
    #     if response.status_code == 200:
    #         return response.json()

    # except Exception as error:
    #     logger.error("get: {}", error)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
             url,
             params=None,
             headers=None, 
             timeout=20) as response:
                logger.debug(response)
                if response.status == 200:
                    if response.content_length > MAX_RESPONSE_SIZE:
                        logger.warning("Response content too large, skipping...")
                        return None  # Return None for large responses
                    return await response.json(content_type=None)

    except Exception as error:
        logger.error("get: {}", error)

