"""
Module for printing and processing all the information about the bot or about actions with this bot
"""
import codecs

# Define all the filenames of HTML info files
START_INFO = "./info/start_info.html"


def get_info(filename: str) -> str:
    """
    Reads an HTML file and returns its content as a string

    :param filename: the filename of an HTML file
    :return: content of the file
    """
    with codecs.open(filename, 'r', 'utf-8') as file:
        return file.read()
