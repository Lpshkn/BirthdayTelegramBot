"""
Module for printing and processing all the information about the bot or about actions with this bot
"""
import codecs
import os
import json


class Localization:
    LANGUAGE_CODE = 'en'

    LANGUAGE_DIRECTORY = os.path.join("./localization", LANGUAGE_CODE)
    INFORMATION_DIRECTORY = os.path.join(LANGUAGE_DIRECTORY, "info")
    MENU_DIRECTORY = os.path.join(LANGUAGE_DIRECTORY, "menu")

    # Define all the information files
    START_INFO = os.path.join(INFORMATION_DIRECTORY, "start_info.html")
    STOP_BOT_INFO = os.path.join(INFORMATION_DIRECTORY, "stop_bot_info.html")

    # Define all the menu files
    MAIN_MENU = os.path.join(MENU_DIRECTORY, "main.json")

    @staticmethod
    def set_language_code(language_code: str):
        """
        This method sets up new language code

        :param language_code:
        :return:
        """
        # Define the language directory containing information in the certain language
        # TODO: Now just English and Russian are available to use
        if language_code == "ru":
            Localization.LANGUAGE_CODE = language_code
        else:
            Localization.LANGUAGE_CODE = "en"

        Localization.LANGUAGE_DIRECTORY = os.path.join("./localization", Localization.LANGUAGE_CODE)
        Localization.INFORMATION_DIRECTORY = os.path.join(Localization.LANGUAGE_DIRECTORY, "info")
        Localization.MENU_DIRECTORY = os.path.join(Localization.LANGUAGE_DIRECTORY, "menu")

        # Define all the information files
        Localization.START_INFO = os.path.join(Localization.INFORMATION_DIRECTORY, "start_info.html")
        Localization.STOP_BOT_INFO = os.path.join(Localization.INFORMATION_DIRECTORY, "stop_bot_info.html")

        # Define all the menu files
        Localization.MAIN_MENU = os.path.join(Localization.MENU_DIRECTORY, "main.json")

    @staticmethod
    def get_info(filename: str) -> str:
        """
        Reads an HTML file and returns its content as a string

        :param filename: the filename of an HTML file
        :return: content of the file
        """
        with codecs.open(filename, 'r', 'utf-8') as file:
            return file.read()

    @staticmethod
    def get_menu(filename: str) -> dict:
        with open(filename) as file:
            return json.load(file)
