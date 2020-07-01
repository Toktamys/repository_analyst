import asyncio
import re
import sys
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BaseAnalyst(ABC):
    _number_open = 0
    _number_closed = 0
    _number_old = 0
    __headers = {
        'Accept': 'application/vnd.github.v3.text-match+json'
    }
    _OPEN = 'open'
    _CLOSED = 'closed'
    _OLD = 'old'

    __query_params = {}
    __base_api = 'https://api.github.com'
    __retries = 5
    _username = ''
    _repository = ''

    def __init__(self, args):
        self._url = args.url
        self._branch = args.branch
        self._start_date = args.start_date
        self._end_date = args.end_date
        self.__set_authorization_token(args.pat)
        self.retry = Retry(total=self.__retries, read=self.__retries, connect=self.__retries, )
        self.adapter = HTTPAdapter(max_retries=self.retry)
        self.check_repository()

    def check_repository(self):
        regex = r"(http|https?:\/\/github.com\/)([\w,\-,\_]+)\/([\w,\-,\_]+)(.git){0,1}(\/){0,1}"
        matches = re.search(regex, self._url, re.IGNORECASE)
        if matches:
            username = matches.groups()[1]
            repo = matches.groups()[2]
            session = requests.Session()
            session.mount('http://', self.adapter)
            session.mount('https://', self.adapter)
            try:
                response = session.get(
                    f'{self.__base_api}/repos/{username}/{repo}', timeout=15, headers=self.__headers
                )
                if response.status_code != 200:
                    raise Exception("Repository doesn't exist")
                response = session.get(
                    f'{self.__base_api}/repos/{username}/{repo}', timeout=15, headers=self.__headers
                )
                if response.status_code != 200:
                    raise Exception("Branch doesn't exist in the repository")
                self._username = username
                self._repository = repo
            except Exception as error:
                print(str(error))
                sys.exit()
        else:
            sys.exit("Invalid repository url")

    @abstractmethod
    def get_tasks_to_fetch(self) -> list:
        raise NotImplementedError

    @abstractmethod
    def handle_response(self, data, state):
        raise NotImplementedError

    @abstractmethod
    def display_result(self):
        raise NotImplementedError

    @classmethod
    def combine_parameters(cls, query_params) -> str:
        result = ''
        for key, value in query_params.items():
            result += f'{key}{value}+'
        return result

    def __set_authorization_token(self, personal_access_token=None):
        if personal_access_token:
            self.__headers['Authorization'] = f'token {personal_access_token}'

    def get_repository_name(self) -> str:
        return f'{self._username}/{self._repository}'

    def fetch(self, session, url, state):
        try:
            response = session.get(url, timeout=15, headers=self.__headers)
            data = response.json()
            return data, state
        except requests.exceptions.RequestException:
            if state:
                return {}, state
            else:
                return [], state

    def get_dates(self, old, bound_date):
        query_params = {}
        if old:
            query_params['created:'] = f'<{bound_date}'
        else:
            if self._start_date and self._end_date:
                query_params['created:'] = f'{self._start_date}..{self._end_date}'
            elif self._start_date and not self._end_date:
                query_params['created:'] = f'{self._start_date}..*'
            elif not self._start_date and self._end_date:
                query_params['created:'] = f'*..{self._end_date}'
        return query_params

    async def get_data_asynchronous(self):
        urls_to_fetch = self.get_tasks_to_fetch()
        if urls_to_fetch:
            with ThreadPoolExecutor(max_workers=10) as executor:
                with requests.Session() as session:
                    session.mount('http://', self.adapter)
                    session.mount('https://', self.adapter)
                    loop = asyncio.get_event_loop()
                    tasks = [
                        loop.run_in_executor(
                            executor,
                            self.fetch,
                            *(session, el[0], el[1])
                        ) for el in urls_to_fetch
                    ]
                    for data, state in await asyncio.gather(*tasks):
                        self.handle_response(data, state)

    def run(self):
        print(f"Start {self} analysis at {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.get_data_asynchronous())
        loop.run_until_complete(future)
        print(f"End {self} analysis at {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

    def get_base_api(self) -> str:
        return self.__base_api
