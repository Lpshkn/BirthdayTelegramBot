"""
Module for all the handlers which will be processed by the ConversationHandler
"""
import telegram
import birthdaybot.menus as menus
from birthdaybot.localization import localization
from telegram.ext import Updater

# Define all the states of the bot
MAIN_MENU, ADD_LISTS = range(2)


def start_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler to /start command. This handler send an localization message to the user.
    """
    chat_id = update.effective_chat.id
    code = update.effective_user.language_code
    context.bot.sendMessage(chat_id=chat_id,
                            text=localization.start_info(code),
                            parse_mode=telegram.ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=menus.get_main_menu(code))

    context.chat_data['title'] = update.effective_chat.title
    context.chat_data['description'] = update.effective_chat.description
    context.chat_data['photo'] = update.effective_chat.photo
    context.chat_data['type'] = update.effective_chat.type

    context.user_data['chat_id'] = chat_id
    context.user_data['username'] = update.effective_user.username
    context.user_data['first_name'] = update.effective_user.first_name
    context.user_data['last_name'] = update.effective_user.last_name
    context.user_data['is_bot'] = update.effective_user.is_bot
    context.user_data['language_code'] = update.effective_user.language_code

    return MAIN_MENU


def stop_bot_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler to /stop command. This handler stops the bot and remove all data about the user
    """
    code = update.effective_user.language_code
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=localization.stop_bot_info(code),
                            parse_mode=telegram.ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=menus.remove_keyboard())

    return telegram.ext.ConversationHandler.END


def main_menu_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler for the main menu. This handler process commands for the main menu.
    """
    # Get language code and get the dictionary of the main menu
    code = update.effective_user.language_code
    main_menu = localization.main_menu(code)

    # Get the text of the message and compare it with the name of buttons
    text = update.message.text
    if text == main_menu[menus.STOP_BOT_BUTTON]:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=localization.stop_bot_info(code),
                                parse_mode=telegram.ParseMode.HTML,
                                disable_web_page_preview=True,
                                reply_markup=menus.remove_keyboard())
        return telegram.ext.ConversationHandler.END

    elif text == main_menu[menus.ADD_LIST_BUTTON]:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=localization.add_lists_info(code),
                                parse_mode=telegram.ParseMode.HTML,
                                disable_web_page_preview=True,
                                reply_markup=menus.accept_cancel_keyboard(code))
        return ADD_LISTS
