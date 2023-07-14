
import requests
from dxsp.config import settings

# ------🛠️ W3 UTILS ---------

async def get(url, params=None, headers=None):
    """ gets a url payload """
    try:
        response = requests.get(
            url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()

    except Exception as error:
        raise error
