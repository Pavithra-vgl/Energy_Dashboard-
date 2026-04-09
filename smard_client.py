import os
import requests

SMARD_BASE_URL = os.getenv("SMARD_BASE_URL", "https://www.smard.de/app")

def fetch_index(filter_id: str, region: str, resolution: str) -> dict:
    """
    SMARD endpoint (documented via OpenAPI):
    /chart_data/{filter}/{region}/index_{resolution}.json
    """
    url = f"{SMARD_BASE_URL}/chart_data/{filter_id}/{region}/index_{resolution}.json"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_series(filter_id: str, region: str, resolution: str, timestamp: int) -> dict:
    # try 1: documented filename pattern
    url1 = f"{SMARD_BASE_URL}/chart_data/{filter_id}/{region}/{filter_id}_{region}_{resolution}_{timestamp}.json"
    r1 = requests.get(url1, timeout=30)
    if r1.status_code == 200:
        return r1.json()

    # try 2: simpler timestamp file (many charts use this)
    url2 = f"{SMARD_BASE_URL}/chart_data/{filter_id}/{region}/{timestamp}.json"
    r2 = requests.get(url2, timeout=30)
    if r2.status_code == 200:
        return r2.json()

    # if both fail, raise the real error
    r1.raise_for_status()

