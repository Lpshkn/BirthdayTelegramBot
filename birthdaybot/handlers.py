"""
Module for all the handlers which will be processed by the ConversationHandler
"""
import telegram
from birthdaybot.info.info import get_info, START_INFO
from telegram.ext import Updater


def start_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler to /start command. This handler send an info message to the user.
    """
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=get_info(START_INFO),
                            parse_mode=telegram.ParseMode.HTML,
                            disable_web_page_preview=True)
