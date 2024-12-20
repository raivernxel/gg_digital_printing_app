import requests
from decouple import config
from django.http import JsonResponse


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
    

def update_trello_api_data(url, params):
    trello_api_key = config('TRELLO_API_KEY')
    trello_api_token = config('TRELLO_TOKEN_KEY')

    params['key'] = trello_api_key
    params['token'] = trello_api_token

    response = requests.put(url, params=params)

    if response.status_code == 200:
        return JsonResponse({'message': 'Card updated successfully', 'data': response.json()})
    else:
        return JsonResponse({'message': 'Failed to update card', 'error': response.text}, status=response.status_code)
    

def get_api(url):
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return e
