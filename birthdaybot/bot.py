"""
Module for all the actions with the Bot
"""
import telegram
import birthdaybot.handlers as handlers
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters


class BirthdayBot:
    def __init__(self, token: str):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def run(self):
        """
        The entrypoint of the bot. Define the ConversationHandler and specify all the handlers.
        """
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', handlers.start_handler)],
            states={

            },
            fallbacks=[]
        )
        self.dispatcher.add_handler(conversation_handler)

        self.updater.start_polling()
        self.updater.idle()
