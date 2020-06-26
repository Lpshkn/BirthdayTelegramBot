"""
Module to build menus for a conversation.
"""
from telegram.keyboardbutton import KeyboardButton
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.replykeyboardremove import ReplyKeyboardRemove
from birthdaybot.localization import localization

# The keys of the buttons
ADD_LIST_BUTTON = "ADD_LIST_BUTTON"
SETTINGS_BUTTON = "SETTINGS_BUTTON"
EDIT_LISTS_BUTTON = "EDIT_LISTS_BUTTON"
STOP_BOT_BUTTON = "STOP_BOT_BUTTON"
ACCEPT_BUTTON = "ACCEPT"
CANCEL_BUTTON = "CANCEL"


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


def get_main_menu(language_code: str):
    """
    Creates a KeyboardMarkup for the main menu and returns it.
    """

    # The dict of the menus
    main_menu = localization.main_menu(language_code)

    button_list = [
        KeyboardButton(main_menu[ADD_LIST_BUTTON]),
        KeyboardButton(main_menu[SETTINGS_BUTTON]),
        KeyboardButton(main_menu[EDIT_LISTS_BUTTON]),
        KeyboardButton(main_menu[STOP_BOT_BUTTON])
    ]

    reply_markup = ReplyKeyboardMarkup(build_menu(button_list, n_cols=1), resize_keyboard=True)
    return reply_markup


def remove_keyboard():
    """
    Creates a RemoveMarkup to remove a keyboard of the bot
    """
    return ReplyKeyboardRemove()


def accept_cancel_keyboard(language_code: str):
    accept_cancel = localization.accept_cancel_menu(language_code)

    button_list = [
        KeyboardButton(accept_cancel[ACCEPT_BUTTON]),
        KeyboardButton(accept_cancel[CANCEL_BUTTON])
    ]

    reply_markup = ReplyKeyboardMarkup(build_menu(button_list, n_cols=1), resize_keyboard=True)
    return reply_markup
