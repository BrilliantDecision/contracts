from api import API
import requests
from unittest import mock

from db import Database


def test_get_urls(mocker):
    mocker.patch('api.API.get_request', return_value=[
        {"url": 'asdf'},
        {"url": 'asdf'},
        {"url": 'asdf'}
    ])
    api = API(token='')
    assert len(api.get_urls({'url_begin': 1, 'url_end': 1}, 6)) == 6


def test_write_contracts(mocker):
    db = Database()
    db.create_connection()
    assert len(db.write_contracts(['tru', 'fdsa', 'qwer'])) == 1


def test_get_contract(mocker):
    mocker.patch('api.API.get_request',
                 side_effect=[
                     {'reg_num': '12345', "documents": [{'url_json': 'asdfasd'}]},
                     {'docDescription': 'решение'}
                 ])
    api = API(token='')
    assert api.get_contract('asdfasdf')['Номер'] == '12345'

