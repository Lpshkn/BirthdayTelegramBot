"""
Module to build menus for a conversation.
"""
from telegram.keyboardbutton import KeyboardButton
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.replykeyboardremove import ReplyKeyboardRemove


ADD_LIST_BUTTON = "Add the list of birthdays"
SETTINGS_BUTTON = "Settings"
EDIT_LISTS_BUTTON = "Edit the lists"
STOP_BOT_BUTTON = "Stop and delete the bot"


def build_menu(buttons, n_cols=1, header_buttons=None, footer_buttons=None):
    """
    Method for building a menu using the list of buttons and the number of columns.

    :param buttons: list of buttons
    :param n_cols: number of columns
    :param header_buttons: use to put buttons in the first row
    :param footer_buttons: use to put buttons in the last row
    :return: menu
    """
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def get_main_menu():
    """
    Creates a KeyboardMarkup for the main menu and returns it.
    """
    button_list = [
        KeyboardButton(ADD_LIST_BUTTON),
        KeyboardButton(SETTINGS_BUTTON),
        KeyboardButton(EDIT_LISTS_BUTTON),
        KeyboardButton(STOP_BOT_BUTTON)
    ]

    reply_markup = ReplyKeyboardMarkup(build_menu(button_list, n_cols=1))
    return reply_markup


def remove_keyboard():
    """
    Creates a RemoveMarkup to remove a keyboard of the bot
    """
    return ReplyKeyboardRemove()
