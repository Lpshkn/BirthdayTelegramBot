"""
Module for all the actions with the Bot
"""
import birthdaybot.handlers as handlers
import logging
from birthdaybot.persistence import BotPersistence
from birthdaybot.db.database import Database
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, PicklePersistence


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class BirthdayBot:
    def __init__(self, token: str, database: Database):
        persistence = BotPersistence(database, store_bot_data=False)

        self.database = database
        self.updater = Updater(token=token, use_context=True, persistence=persistence)
        self.dispatcher = self.updater.dispatcher

    def run(self):
        """
        The entrypoint of the bot. Define the ConversationHandler and specify all the handlers.
        """
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', handlers.start_handler)],
            states={
                handlers.MAIN_MENU: [MessageHandler(Filters.text & ~Filters.command, handlers.main_menu_handler)]
            },
            fallbacks=[CommandHandler('stop', handlers.stop_bot_handler)],

            name="main_menu_state",
            persistent=True,
            per_user=False
        )
        self.dispatcher.add_handler(conversation_handler)

        self.updater.start_polling()
        self.updater.idle()

