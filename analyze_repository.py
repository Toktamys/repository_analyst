"""
Script for Github repository analyze
"""
from classes.argument_parser import ArgumentParser
from classes.client import Client


def main():
    args = ArgumentParser.get_arguments()
    client = Client(args)
    client.run()
    client.display_result()


if __name__ == '__main__':
    main()
