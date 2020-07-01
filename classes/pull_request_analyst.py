from datetime import timedelta, datetime

from classes.base_analyst import BaseAnalyst


class PullRequestAnalyst(BaseAnalyst):
    __MAX_DAYS_OFFSET = 30
    __query_params = {}

    def __init__(self, args):
        super().__init__(args)
        self.bound_date = self.__set_bound_date()
        self.set_query_params()

    def __set_bound_date(self):
        return (datetime.now() - timedelta(days=self.__MAX_DAYS_OFFSET)).strftime('%Y-%m-%d')

    def set_query_params(self):
        self.__query_params['repo:'] = self.get_repository_name()
        self.__query_params['is:'] = 'pr'
        self.__query_params['base:'] = self._branch

    def get_tasks_to_fetch(self) -> list:
        return [
            (self.get_fetch_url(self._OPEN), self._OPEN),
            (self.get_fetch_url(self._CLOSED), self._CLOSED),
            (self.get_fetch_url(self._OPEN, old=True), self._OLD),
        ]

    def get_fetch_url(self, state, old=False) -> str:
        query_params = self.__query_params
        query_params['state:'] = state
        query_params.update(self.get_dates(old, self.bound_date))
        return f'{self.get_base_api()}/search/issues?q={self.combine_parameters(query_params)}'

    def display_result(self):
        print("Result of pull requests analysis")
        text = f"Number of open pull requests - {self._number_open}\n"
        text += f"Number of closed pull requests - {self._number_closed}\n"
        text += f"Number of 'old' pull requests - {self._number_old}\n"
        print(text, end="\n")

    def handle_response(self, data, state):
        if state == self._OPEN:
            self._number_open = data.get('total_count', 'N/A')
        elif state == self._CLOSED:
            self._number_closed = data.get('total_count', 'N/A')
        elif state == self._OLD:
            self._number_old = data.get('total_count', 'N/A')

    def __str__(self):
        return 'Pull Request'
