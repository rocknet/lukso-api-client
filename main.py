import argparse
import time
from typing import NamedTuple
from urllib.parse import urlencode
import requests
import pandas as pd

class ApiResponse(NamedTuple):
    items: pd.DataFrame
    next_page_params: str
    
def fetch_data_from_api(url: str) -> ApiResponse:
    response = requests.get(url)
    data = response.json()
    df = pd.json_normalize(data["items"])
    next_page_params = data.get('next_page_params', None)
    return ApiResponse(df, next_page_params)


def fetch_all_data(base_url: str):
    all_data = pd.DataFrame()
    next_page_params = {}

    while True:
        url = base_url
        if next_page_params:
            query_string = urlencode(next_page_params)
            url = f"{base_url}?{query_string}"

        time.sleep(2)
        response = fetch_data_from_api(url)
        print(response.next_page_params)

        all_data = pd.concat([all_data, response.items])

        if not response.next_page_params:
            break

        next_page_params = response.next_page_params

    return all_data

parser = argparse.ArgumentParser()
parser.add_argument("address")
args = parser.parse_args()

base_url = f'https://explorer.execution.mainnet.lukso.network/api/v2/addresses/{args.address}/withdrawals'
all_data = fetch_all_data(base_url)
all_data["amount"] = all_data['amount'].astype(float) / (10**18)
