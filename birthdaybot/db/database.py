"""
This module implements the database interaction and other methods to provide getting data easier.
"""
import psycopg2
import sys
from psycopg2 import sql


class Database:
    def __init__(self, json_obj):
        self._name = json_obj["PG_NAME"]
        self._user = json_obj["PG_USER"]
        self._password = json_obj["PG_PSWD"]
        self._host = json_obj["PG_HOST"]
        self._port = json_obj["PG_PORT"]

        self.connection = self._connect()
        self.connection.autocommit = True

        self._create_tables()

    def _connect(self):
        try:
            connection = psycopg2.connect(database=self._name,
                                          user=self._user,
                                          password=self._password,
                                          host=self._host,
                                          port=self._port)

            return connection
        except psycopg2.OperationalError as e:
            print("Error: {}".format(e), file=sys.stderr)
            exit(-2)

    def _create_tables(self):
        """
        Creates tables if they don't exist.
        """
        with self.connection.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS Chats ("
                        "chat_id integer CONSTRAINT chats_pkey PRIMARY KEY);")

            cur.execute("CREATE TABLE IF NOT EXISTS Conversations ("
                        "chat_id integer CONSTRAINT conversations_pkey PRIMARY KEY REFERENCES chats "
                        "ON DELETE CASCADE ON UPDATE CASCADE,"
                        "main_menu_state integer NULL);")

            cur.execute("CREATE TABLE IF NOT EXISTS Users ("
                        "user_id integer CONSTRAINT users_pkey PRIMARY KEY,"
                        "chat_id integer REFERENCES Chats ON DELETE SET NULL ON UPDATE CASCADE,"
                        "username varchar(32) NOT NULL UNIQUE);")

            cur.execute("CREATE TABLE IF NOT EXISTS Notes ("
                        "note_id integer CONSTRAINT notes_pkey PRIMARY KEY,"
                        "chat_id integer REFERENCES Chats ON DELETE CASCADE ON UPDATE CASCADE,"
                        "datetime timestamp(0) NOT NULL UNIQUE);")

    def update_conversation(self, conversations: dict, name: str = None, key: tuple = None):
        """
        Method updates a conversation's state in the database.

        :param name: the name of a Conversation handler
        :param conversations: a dictionary containing chat_id and conversation state
        :param key: chat_id
        """
        self.add_chats(conversations, name)

        if name and key:
            chat_id = key[0]
            with self.connection.cursor() as cur:
                query = sql.SQL("INSERT INTO conversations(chat_id, {0}) VALUES ({1}, {2})"
                                "ON CONFLICT (chat_id) DO UPDATE SET {0} = excluded.{0}").format(
                    sql.Identifier(name), sql.Literal(chat_id), sql.Literal(conversations[name][key])
                )
                cur.execute(query)
        else:
            with self.connection.cursor() as cur:
                for key, value in conversations["main_menu_state"].items():
                    chat_id = key[0]
                    query = sql.SQL("INSERT INTO conversations(chat_id, main_menu_state) VALUES ({0}, {1})"
                                    "ON CONFLICT (chat_id) DO UPDATE SET main_menu_state = excluded.main_menu_state").format(
                        sql.Literal(chat_id), sql.Literal(value)
                    )
                    cur.execute(query)

    def add_chats(self, conversations: dict, name: str = None):
        """
        Method to add chat_ids into the database.

        :param conversations: a dictionary containing chat_id and conversation state
        :param name: the name of a Conversation handler
        """
        if not name:
            name = "main_menu_state"

        with self.connection.cursor() as cur:
            for key in conversations[name].keys():
                chat_id = key[0]
                query = sql.SQL("INSERT INTO chats(chat_id) VALUES ({0})"
                                "ON CONFLICT (chat_id) DO NOTHING").format(sql.Literal(chat_id))
                cur.execute(query)
