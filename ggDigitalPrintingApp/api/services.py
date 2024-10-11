import requests
from decouple import config


def get_trello_api_data(url):
    trello_api_key = config('TRELLO_API_KEY')
    trello_api_token = config('TRELLO_TOKEN_KEY')
    api_url = url

    params = {
        'key': trello_api_key,
        'token': trello_api_token
    }

    try:
        response = requests.get(api_url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return e
