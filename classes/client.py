from classes.contributor_analyst import ContributorAnalyst
from classes.issue_analyst import IssueAnalyst
from classes.pull_request_analyst import PullRequestAnalyst


class Client:
    __analyst_list = []

    def __init__(self, args):
        self.__analyst_list.append(ContributorAnalyst(args))
        self.__analyst_list.append(PullRequestAnalyst(args))
        self.__analyst_list.append(IssueAnalyst(args))

    def run(self):
        print("Processing ... ")
        for analyst in self.__analyst_list:
            analyst.run()

    def display_result(self):
        for analyst in self.__analyst_list:
            analyst.display_result()
