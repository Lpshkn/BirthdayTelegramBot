"""
Module for all the handlers which will be processed by the ConversationHandler
"""
import telegram
import birthdaybot.menus as menus
from birthdaybot.localization import localization
from telegram.ext import Updater
from birthdaybot.localization.localization import Localization

# Define all the states of the bot
MAIN_MENU = range(1)


def start_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler to /start command. This handler send an localization message to the user.
    """
    code = update.effective_user.language_code
    Localization.set_language_code(code)

    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=localization.Localization.get_info(Localization.START_INFO),
                            parse_mode=telegram.ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=menus.get_main_menu())

    return MAIN_MENU


def stop_bot_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler to /stop command. This handler stops the bot and remove all data about the user
    """
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=localization.Localization.get_info(Localization.STOP_BOT_INFO),
                            parse_mode=telegram.ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=menus.remove_keyboard())

    return telegram.ext.ConversationHandler.END
