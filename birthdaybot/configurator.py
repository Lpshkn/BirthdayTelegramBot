"""
This module represents a configurator which will set any configurations,
get and process the parameters received from the command line
"""
from argparse import ArgumentParser


class Configurator:
    def __init__(self, args):
        # Set descriptions of the program
        description = "This is a bot which will unobtrusively remind users about their friends' birthday!"
        program_name = "birthdaybot"
        epilog = "Lpshkn, 2020"
        self._parser = self._get_parser(program_name, description, epilog)

        # Get parameters from the arguments received from the command line
        self._parameters = self._get_parameters(args)

    @staticmethod
    def _get_parser(program_name: str = None, description: str = None, epilog: str = None) -> ArgumentParser:
        """
        Method creates the instance of the ArgumentParser class, adds arguments in here and returns that instance.

        :param program_name: name of the program
        :param description: description of the program
        :param epilog: epilog of the program
        :return: an instance of the ArgumentParser class
        """

        parser = ArgumentParser(prog=program_name, description=description, epilog=epilog)

        parser.add_argument('token',
                            help='The token to work with the bot.',
                            type=str)

        return parser

    def _get_parameters(self, args):
        """
        This method gets all parameters from the args of the command line.

        :param args: list of the arguments of the command line
        :return: parsed arguments
        """
        parameters = self._parser.parse_args(args)

        return parameters

    def get_token(self) -> str:
        """
        Returns the token to work with the bot.

        :return: token
        """

        return self._parameters.token
