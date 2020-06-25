"""
Module for printing and processing all the information about the bot or about actions with this bot
"""
import codecs
import os
import json


def _get_info(filename: str) -> str:
    """
    Reads an HTML file and returns its content as a string

    :param filename: the filename of an HTML file
    :return: content of the file
    """
    with codecs.open(filename, 'r', 'utf-8') as file:
        return file.read()


def _get_menu(filename: str) -> dict:
    with open(filename) as file:
        return json.load(file)


def get_language_code(language_code: str):
    # Define the language directory containing information in the certain language
    # TODO: Now just English and Russian are available to use

    if language_code == "ru":
        return language_code
    else:
        return "en"


# Localization files
def start_info(language_code: str):
    return _get_info(os.path.join("./localization", get_language_code(language_code), "info", "start_info.html"))


def stop_bot_info(language_code: str):
    return _get_info(os.path.join("./localization", get_language_code(language_code), "info", "stop_bot_info.html"))


def main_menu(language_code: str):
    return _get_menu(os.path.join("./localization", get_language_code(language_code), "menu", "main.json"))
