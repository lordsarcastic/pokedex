from typing import Any, Dict

import requests


def make_request(url, **kwargs) -> Dict[Any, Any]:
    """
    Non-generic utility to make a request to the given URL.
    """
    response = requests.get(url, **kwargs)
    response.raise_for_status()
    return response.json()
