"""
Module for printing and processing all the information about the bot or about actions with this bot
"""
import codecs
import os

# Define the language directory containing information in the certain language
ENGLISH = "en"
LANGUAGE_DIRECTORY = os.path.join("./info", ENGLISH)

# Define all the filenames of HTML info files
START_INFO = os.path.join(LANGUAGE_DIRECTORY, "start_info.html")
STOP_BOT_INFO = os.path.join(LANGUAGE_DIRECTORY, "stop_bot_info.html")


def get_info(filename: str) -> str:
    """
    Reads an HTML file and returns its content as a string

    :param filename: the filename of an HTML file
    :return: content of the file
    """
    with codecs.open(filename, 'r', 'utf-8') as file:
        return file.read()
