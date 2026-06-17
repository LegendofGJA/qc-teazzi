import requests
from core.config import NETWORK_TIMEOUT


def is_online():
    try:
        requests.head(
            "https://www.google.com", timeout=NETWORK_TIMEOUT, allow_redirects=False
        )
        return True
    except Exception:
        return False


def check_github_reachable():
    try:
        requests.head(
            "https://raw.githubusercontent.com", timeout=NETWORK_TIMEOUT
        )
        return True
    except Exception:
        return False


def check_jsonblob_reachable():
    try:
        requests.head(
            "https://jsonblob.com", timeout=NETWORK_TIMEOUT
        )
        return True
    except Exception:
        return False
