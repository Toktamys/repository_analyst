from argparse import ArgumentParser as BaseArgumentParser


class ArgumentParser:

    @classmethod
    def get_arguments(cls):
        parser = BaseArgumentParser()
        parser.add_argument('url', type=str, help='URL of public repository')

        parser.add_argument('--branch', required=False, type=str, default='master',
                            help='Repository branch. Optional argument. Default is master')

        parser.add_argument(
            '--start_date',
            required=False,
            type=str,
            default=None,
            help='Analysis start date. Optional argument. Default is None. Format dd.mm.yyyy'
        )

        parser.add_argument(
            '--end_date',
            required=False,
            type=str,
            default=None,
            help='Analysis end date. Optional argument. Default is None. Format dd.mm.yyyy'
        )

        parser.add_argument(
            '--pat', required=False, type=str, default=None,
            help='Personal access token. Optional argument. Default is None')

        args = parser.parse_args()
        return args
