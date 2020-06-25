"""
Module for all the actions with the Bot
"""
import birthdaybot.handlers as handlers
import logging
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, PicklePersistence


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class BirthdayBot:
    def __init__(self, token: str, persistence_filename: str = None):
        if persistence_filename:
            persistence = PicklePersistence(persistence_filename)
        else:
            logging.warning("There is no persistence file to save the states of a conversation or any data!")
            persistence = None

        self.updater = Updater(token=token, use_context=True, persistence=persistence)
        self.dispatcher = self.updater.dispatcher

    def run(self):
        """
        The entrypoint of the bot. Define the ConversationHandler and specify all the handlers.
        """
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', handlers.start_handler)],
            states={
                handlers.MAIN_MENU: [
                    MessageHandler(Filters.text & ~Filters.command, handlers.main_menu_handler)
                ]
            },
            fallbacks=[CommandHandler('stop', handlers.stop_bot_handler)],

            name="main_conversation",
            persistent=True
        )
        self.dispatcher.add_handler(conversation_handler)

        self.updater.start_polling()
        self.updater.idle()

