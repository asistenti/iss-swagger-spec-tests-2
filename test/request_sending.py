import requests

from urllib.parse import urlencode


def send_post_request(data, url, query_params=None, jwt=None):
    headers = {'Content-type': 'application/json'}
    if jwt is not None:
        headers['authorization'] = f'Bearer {jwt}'
    if query_params is not None:
        url = f'{url}?{urlencode(query_params)}'
    return requests.post(url=url, json=data, headers=headers)


def send_get_request(url, query_params=None, jwt=None):
    headers = {'Content-type': 'application/json'}
    if jwt is not None:
        headers['authorization'] = f'Bearer {jwt}'
    if query_params is not None:
        url = f'{url}?{urlencode(query_params)}'
    return requests.get(url=url, headers=headers)


def send_put_request(data, url, query_params=None, jwt=None):
    headers = {'Content-type': 'application/json'}
    if jwt is not None:
        headers['authorization'] = f'Bearer {jwt}'
    if query_params is not None:
        url = f'{url}?{urlencode(query_params)}'
    if data is not None:
        return requests.put(url=url, json=data, headers=headers)
    else:
        return requests.put(url=url, headers=headers)


def send_delete_request(url, query_params=None, jwt=None):
    headers = {'Content-type': 'application/json'}
    if jwt is not None:
        headers['authorization'] = f'Bearer {jwt}'
    if query_params is not None:
        url = f'{url}?{urlencode(query_params)}'
    return requests.delete(url=url, headers=headers)
