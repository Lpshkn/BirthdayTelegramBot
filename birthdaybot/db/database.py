"""
This module implements the database interaction and other methods to provide getting data easier.
"""
import psycopg2
import logging
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
            # Create the enum for the type of a chat
            cur.execute("DO $$ "
                        "BEGIN "
                        "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'chat_type') THEN "
                        "CREATE TYPE chat_type AS ENUM ('private', 'group', 'channel', 'supergroup'); "
                        "END IF; "
                        "END $$;")

            cur.execute("CREATE TABLE IF NOT EXISTS Chats ("
                        "chat_id integer CONSTRAINT chats_pkey PRIMARY KEY,"
                        "title varchar(256),"
                        "description varchar(256),"
                        "photo varchar(1000),"
                        "type chat_type);")

            cur.execute("CREATE TABLE IF NOT EXISTS Conversations ("
                        "chat_id integer CONSTRAINT conversations_pkey PRIMARY KEY REFERENCES chats "
                        "ON DELETE CASCADE ON UPDATE CASCADE,"
                        "main_menu_state integer NULL);")

            cur.execute("CREATE TABLE IF NOT EXISTS Users ("
                        "user_id integer CONSTRAINT users_pkey PRIMARY KEY,"
                        "chat_id integer REFERENCES Chats ON DELETE SET NULL ON UPDATE CASCADE,"
                        "username varchar(32),"
                        "first_name varchar(256),"
                        "last_name varchar(256),"
                        "is_bot boolean,"
                        "language_code varchar(10) DEFAULT 'en');")

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

    def get_conversation(self, name: str) -> dict:
        """
        Method gets conversation states from the database.

        This method returns a dictionary consisting of a tuple and a state of the handler.
        The tuple contains the chat_id. It returns a tuple because of the handler requires it and besides the chat_id,
        the user_id and the message_id may be passed. But now it isn't required and just user_id will be sent.
        This fact may be changed in the ConversationHandler constructor (parameters per_chat, per_user, per_message)

        :param name: the name of a Conversation handler
        :return: dictionary
        """
        with self.connection.cursor() as cur:
            query = sql.SQL("SELECT chat_id, {} FROM conversations").format(sql.Identifier(name))
            cur.execute(query)
            return {(chat_id,): state for (chat_id, state) in cur.fetchall()}

    def get_chat_data(self) -> dict:
        """
        Method to getting chat_data from the database.
        Returns dictionary containing the chat_id and a list of arguments.

        :return: dictionary
        """
        return self.get_data("chats")

    def get_user_data(self) -> dict:
        """
        Method to getting user_data from the database.
        Returns dictionary containing the user_id and a list of arguments.

        :return: dictionary
        """
        return self.get_data("users")

    def get_data(self, table_name: str) -> dict:
        """
        Method builds a query to get all data from the table of the database.

        :param table_name: the name of a table
        :return: dictionary containing id and a list of arguments
        """
        with self.connection.cursor() as cur:
            query = sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_name = {};").format(
                sql.Literal(table_name))
            cur.execute(query)

            columns = [column[0] for column in cur.fetchall()]

            if not columns:
                logging.warning("The names of columns from the Chats table weren't received")
                return {}

            # Get all data and create a dictionary
            query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
            cur.execute(query)
            data = cur.fetchall()

            if data:
                return {row[0]: {columns[i]: row[i] for i in range(1, len(columns))} for row in data}
            else:
                return {}

    def update_data(self, table_name: str, data: dict):
        """
        Method builds a query to update all data of the table of the database.

        :param table_name: the name of a table
        :param data: dictionary containing ids and a list of arguments with it
        """
        if data:
            # Iterate through all ids
            for id, data_dict in data.items():
                with self.connection.cursor() as cur:
                    # Get all the names of the columns of the table
                    query = sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_name = {};").format(
                        sql.Literal(table_name))
                    cur.execute(query)
                    columns = [column[0] for column in cur.fetchall()]

                    # Build a list containing all values of this id
                    values = [id]
                    values.extend(data[id][column] for column in columns[1:])

                    if not columns:
                        logging.warning("The names of columns from the {} table weren't received".format(table_name))
                        return {}

                    # Build the SQL-string to use "UPSERT" function
                    setting_columns = list(map(lambda x: sql.SQL("{0} = excluded.{0}").format(sql.Identifier(x)), columns[1:]))

                    # Build a query
                    query = sql.SQL("INSERT INTO {0}({1}) "
                                    "VALUES ({2}) "
                                    "ON CONFLICT ({3}) DO UPDATE SET "
                                    "{4}").format(
                        sql.Identifier(table_name),
                        sql.SQL(',').join(map(sql.Identifier, columns)),
                        sql.SQL(',').join(map(sql.Literal, values)),
                        sql.Identifier(columns[0]),
                        sql.SQL(',').join(setting_columns))
                    cur.execute(query)

    def update_chat_data(self, chat_data: dict):
        """
        Method updates the data of chats in the database (if it was changed).

        :param chat_data: a new data
        """
        self.update_data('chats', chat_data)

    def update_user_data(self, user_data: dict):
        """
        Method updates the data of users in the database (if it was changed).

        :param user_data:
        :return:
        """
        self.update_data('users', user_data)


