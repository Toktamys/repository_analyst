from datetime import datetime
from functools import reduce
from time import mktime

from classes.base_analyst import BaseAnalyst


class ContributorAnalyst(BaseAnalyst):
    __contributors = []

    def get_tasks_to_fetch(self) -> list:
        return [(self.get_fetch_url(), None)]

    def get_fetch_url(self):
        return f'{self.get_base_api()}/repos/{self.get_repository_name()}/stats/contributors'

    def __get_date_range(self):
        start_date = None
        end_date = None
        if self._start_date:
            start_date = mktime(datetime.strptime(self._start_date, '%Y-%m-%d').timetuple())
        if self._end_date:
            end_date = mktime(datetime.strptime(self._end_date, '%Y-%m-%d').timetuple())
        return start_date, end_date

    @classmethod
    def filter_weeks(cls, item, start_date, end_date):
        if start_date and end_date:
            return start_date <= item['w'] < end_date and item['c'] > 0
        elif start_date and not end_date:
            return item['w'] >= start_date and item['c'] > 0
        elif not start_date and end_date:
            return item['w'] <= end_date and item['c'] > 0
        else:
            return item['w'] > 0

    def __parse_result(self, contributors):
        self.__contributors = []
        data = []
        start_date, end_date = self.__get_date_range()
        if contributors:
            for contributor in contributors:
                weeks = [
                    item
                    for item in contributor['weeks'] if self.filter_weeks(item, start_date, end_date)
                ]
                commit_count = reduce(lambda x, y: x + y['c'], weeks, 0)
                data.append({
                    'login': contributor['author'].get('login', 'Not defined'),
                    'commit_count': commit_count
                })
            data = sorted(data, key=lambda x: x['commit_count'], reverse=True)
            data = list(filter(lambda x: x['commit_count'] > 0, data))
            self.__contributors = data[:30]

    def handle_response(self, data, state):
        self.__parse_result(data)

    def __str__(self):
        return 'Contributors'

    def display_result(self):
        print("\nTHE LIST OF MOST ACTIVE CONTRIBUTORS\n")
        if self.__contributors:
            print("{:>5}|{:<20}|{:<13}|".format('#', 'Login', 'Commits count'))
            for idx, contributor in enumerate(self.__contributors, start=1):
                print("{:>5}|{:<20}|{:>13}|".format(
                    idx,
                    contributor['login'],
                    contributor['commit_count']
                ))
            print("\n")
        else:
            print("No data\n")
