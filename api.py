import requests
from requests.exceptions import Timeout, ConnectionError
from datetime import datetime, timedelta
import pytz
import time


class API:
    FILTER_WORDS_ZAKUPKA = ['уклонивши', 'отказ']
    FILTER_WORDS_CONTRACT = ['уклон', 'отказ', 'решен', 'односторон', 'признан']
    NAME_ZAKUPKA = ['223', 'fz44']
    STATE_ZAKUPKA = ['completed', 'cancelled']
    TIMEOUT_GET = 15
    TIMEBREAK_SLEEP = 0.7
    DOC_LIMIT = 20
    DOCS_PER_PAGE = 50
    CONTRACTS_LIMIT = 50
    ZAKUPKI_LIMIT = 0
    CONTRACT_URL_NAME = 'contracts'
    ZAKUPKI_URL_NAME = 'zakupki'

    token = None
    requestNum = 0

    def __init__(self, token):
        self.token = token


    def do_timebreak(self):
        # WARNING! Only 100 rpm!
        time.sleep(self.TIMEBREAK_SLEEP)


    def get_request(self, url):
        self.requestNum += 1
        print(f'Число запросов: {self.requestNum}')
        while True:
            try:
                data = requests.get(
                    url,
                    headers={
                        'Authorization': f'Bearer {self.token}',
                        'Accept': 'application/json'
                    }, timeout=self.TIMEOUT_GET
                ).json()
                self.do_timebreak()
                return data
            except ConnectionError:
                pass


    def item_generator(self, json_input, lookup_key):
        if isinstance(json_input, dict):
            for k, v in json_input.items():
                if k == lookup_key:
                    yield v
                else:
                    yield from self.item_generator(v, lookup_key)
        elif isinstance(json_input, list):
            for item in json_input:
                yield from self.item_generator(item, lookup_key)


    def get_urls(self, obj, limit):
        url_begin = obj['url_begin']
        url_end = obj['url_end']
        page = 1
        items = []

        while True:
            if len(items) >= limit:
                break

            try:
                url = f'{url_begin}{page}{url_end}'
                data = self.get_request(url)
            except Timeout:
                continue

            items += data

            if len(data) < self.DOCS_PER_PAGE:
                break

            page += 1

        urls = []

        for i in items:
            try:
                urls.append(i['url'])
            except KeyError:
                continue

        return urls


    def get_all_urls(self, ):
        time_zone_moscow = pytz.timezone("Europe/Moscow")
        time_now = datetime.now(tz=time_zone_moscow)
        hours_now = time_now.hour

        if hours_now < 6:
            hours_delta = hours_now + 18
        else:
            hours_delta = hours_now - 6

        timeshift_zakupki = hours_delta
        timeshift_contracts = hours_delta

        time_moscow_zakupki = (datetime.now(tz=time_zone_moscow) -
                               timedelta(hours=timeshift_zakupki) - timedelta(hours=hours_now)).isoformat()
        time_moscow_contracts = (datetime.now(tz=time_zone_moscow) -
                                 timedelta(hours=timeshift_contracts)).isoformat()
        params = {
            'url_begin': None,
            'url_end': f'&per={self.DOCS_PER_PAGE}'
        }
        urls_zakupka = []

        for name in self.NAME_ZAKUPKA:
            for state in self.STATE_ZAKUPKA:
                url_begin = f'https://{name}.gosplan.info/api/v1/purchases/?state={state}' \
                            f'&purchase_updated_at_after={time_moscow_zakupki}&page= '
                params['url_begin'] = url_begin
                urls_zakupka += self.get_urls(params, self.ZAKUPKI_LIMIT)

        url_begin_contract = f'https://fz44.gosplan.info/api/v1/contracts/?updated_at_after={time_moscow_contracts}&' \
                             f'stage=ET&page='
        params['url_begin'] = url_begin_contract
        urls_contract = self.get_urls(params, self.CONTRACTS_LIMIT)

        urls = {
            # ZAKUPKI_URL_NAME: urls_zakupka,
            self.CONTRACT_URL_NAME: urls_contract
        }

        return urls


    def get_contract(self, url):
        try:
            data = self.get_request(url)
        except Timeout:
            return None

        try:
            documents = data.get('documents')
            num = data['reg_num']
        except KeyError:
            return None

        if len(documents) > self.DOC_LIMIT:
            return None

        document_urls = []
        contract = {
            'Номер': num
        }

        for d in documents:
            try:
                document_urls.append(d['url_json'])
            except KeyError:
                continue

        for document_url in document_urls:
            try:
                doc_data = self.get_request(document_url)
            except Timeout:
                continue

            for doc_name in self.item_generator(doc_data, 'docDescription'):
                for word in self.FILTER_WORDS_CONTRACT:
                    if word in doc_name.lower():
                        return contract

        return None

    def is_bad_token(self, ):
        url = 'https://fz44.gosplan.info/api/v1/contracts/?page=0'

        try:
            data = requests.get(
                url,
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Accept': 'application/json'
                },
                timeout=self.TIMEOUT_GET
            )
        except Timeout:
            return 'Неполадки на сервере!'
        except ConnectionError:
            return 'Проверьте интернет соединение!'

        if data.status_code == 200:
            self.do_timebreak()
            return None
        else:
            return 'Введите верный токен!'
