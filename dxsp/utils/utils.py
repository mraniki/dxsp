"""
 DEX SWAP
🛠️ W3 UTILS
"""

import aiohttp
from loguru import logger


async def fetch_url(url, params=None, headers=None):
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
    max_response_size = 10 * 1024 * 1024  # 10 MB
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, params=params, headers=headers, timeout=20
            ) as response:
                if response.status == 200:
                    if (
                        response.content_length
                        and response.content_length > max_response_size
                    ):
                        logger.warning("Response content is too large to process.")
                        return None
                    return await response.json(content_type=None)
                logger.warning(f"Received non-200 status code: {response.status}")
    except Exception as error:
        logger.error(f"Unexpected error occurred: {error}")
    return None
