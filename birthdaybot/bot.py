"""
Module for all the actions with the Bot
"""
import telegram
import birthdaybot.handlers as handlers
import logging
import birthdaybot.menus as menus
from birthdaybot.localization import localization
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

        self.entries = {}

    def run(self):
        """
        The entrypoint of the bot. Define the ConversationHandler and specify all the handlers.
        """
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', handlers.start_handler)],
            states={
                handlers.MAIN_MENU: [MessageHandler(Filters.text & ~Filters.command, handlers.main_menu_handler)],
                handlers.ADD_LISTS: [MessageHandler(Filters.text & ~Filters.command, self.add_lists_handler)]
            },
            fallbacks=[CommandHandler('stop', handlers.stop_bot_handler)],

            name="main_menu_state",
            persistent=True,
            per_user=False
        )
        self.dispatcher.add_handler(conversation_handler)

        self.updater.start_polling()
        self.updater.idle()

    def add_lists_handler(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        # Get language code and get the dictionary of the main menu
        code = update.effective_user.language_code
        accept_cancel_menu = localization.accept_cancel_menu(code)
        chat_id = update.effective_chat.id

        # Get the text of the message and compare it with the name of buttons
        text = update.message.text

        # If the user pressed the 'Cancel' button
        if text == accept_cancel_menu[menus.CANCEL_BUTTON]:
            # Remove the list of entries
            if chat_id in self.entries:
                self.entries.pop(chat_id)
            context.bot.sendMessage(chat_id=chat_id,
                                    text=localization.cancel(code),
                                    reply_markup=menus.get_main_menu(code))
            return handlers.MAIN_MENU

        # If the user pressed the 'Accept' button
        elif text == accept_cancel_menu[menus.ACCEPT_BUTTON]:
            pass

        # If the user sends a message
        else:
            entries = handlers.process_entries(text, update, context)
            self.entries.setdefault(chat_id, set())
            self.entries[chat_id] |= entries
