"""
 DEX SWAP
🛠️ W3 UTILS
"""

import aiohttp
from loguru import logger

#todo: move to config
MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # Maximum response size in bytes (e.g., 5 MB)


async def get(url, params=None, headers=None):
    """
    Asynchronously gets a url payload
    and returns the response.

    Args:
        url (str): The url to get.
        params (dict, optional): The params to send. Defaults to None.
        headers (dict, optional): The headers to send. Defaults to None.

    Returns:
        dict or None: The response or None if an 
        error occurs or the response is too large.

    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, params=params, headers=headers, timeout=20) as response:
                if response.status == 200:
                    # Check if content_length is not None and does not exceed the limit
                    if (response.content_length is not None 
                        and response.content_length > MAX_RESPONSE_SIZE):
                        logger.warning("Response content too large, skipping...")
                        return None
                    else:
                        return await response.json(content_type=None)
                else:
                    logger.warning(f"Non-200 status code received: {response.status}")
                    return None
    except aiohttp.ClientError as client_error:
        logger.error(f"Client error occurred: {client_error}")
    except aiohttp.http_exceptions.HttpProcessingError as http_error:
        logger.error(f"HTTP processing error occurred: {http_error}")
    except Exception as error:
        logger.error(f"Unexpected error occurred: {error}")
    return None  # Return None in case of any error.