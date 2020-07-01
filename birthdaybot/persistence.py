"""
This method implements the inheritance from the BasePersistence class to provide the persistence of the bot.
"""
from birthdaybot.db.database import Database
from telegram.ext import BasePersistence
from collections import defaultdict
from copy import deepcopy


class BotPersistence(BasePersistence):
    def __init__(self, database: Database,
                 store_user_data=True,
                 store_chat_data=True,
                 store_bot_data=True,
                 on_flush=False):
        super(BotPersistence, self).__init__(store_user_data=store_user_data,
                                             store_chat_data=store_chat_data,
                                             store_bot_data=store_bot_data)
        self.database = database
        self.on_flush = on_flush
        self.user_data = None
        self.chat_data = None
        self.bot_data = None
        self.conversations = None

    def get_user_data(self):
        pass

    def get_chat_data(self) -> dict:
        """
        Returns the chat_data from the database.

        :return: The restored chat data.
        """
        if self.chat_data:
            pass
        else:
            data = self.database.get_chat_data()
            if not data:
                data = defaultdict(dict)
            else:
                data = defaultdict(dict, data)
            self.chat_data = data

        return deepcopy(self.chat_data)

    def get_bot_data(self):
        pass

    def get_conversations(self, name):
        if self.conversations:
            pass
        else:
            data = self.database.get_conversation(name)
            if not data:
                data = {}
            self.conversations = data

        return self.conversations.copy()

    def update_bot_data(self, data):
        pass

    def update_chat_data(self, chat_id, data):
        pass

    def update_user_data(self, user_id, data):
        pass

    def update_conversation(self, name: str, key: tuple, new_state: int):
        """
        Will update the conversations for the given handler and depending on :attr:`on_flush`
        save data in the database.

        :param name: The handlers name.
        :param key: The key the state is changed for.
        :param new_state: The new state for the given key.
        """
        # Since, this bot can't be invited into a group, it has just chat_id (as key) and will have no name
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return

        self.conversations[name][key] = new_state

        if not self.on_flush:
            self.database.update_conversation(self.conversations, name, key=key)

    def flush(self):
        if self.user_data:
            pass
        if self.chat_data:
            pass
        if self.bot_data:
            pass
        if self.conversations:
            self.database.update_conversation(self.conversations)

        self.database.connection.close()

