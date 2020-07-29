"""
This module implements the database interaction and other methods to provide getting data easier.
"""
import datetime as dt
import logging
from birthdaybot.db.db_connection import DatabaseConnection
from collections import defaultdict
from psycopg2 import sql

NOTIFY_INSERT_NOTES = 'insert_notes'
NOTIFY_UPDATE_NOTES = 'update_notes'
NOTIFY_DELETE_NOTES = 'delete_notes'


class Database(DatabaseConnection):
    def __init__(self, json_obj):
        super().__init__(json_obj)
        self.connection.autocommit = True
        self._create_tables()

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

            cur.execute("CREATE TABLE IF NOT EXISTS Conversations ("
                        "chat_id integer CONSTRAINT conversations_pkey PRIMARY KEY,"
                        "main_menu_state integer NULL);")

            cur.execute("CREATE TABLE IF NOT EXISTS Chats ("
                        "chat_id integer CONSTRAINT chats_pkey PRIMARY KEY REFERENCES conversations "
                        "ON DELETE CASCADE ON UPDATE CASCADE,"
                        "title varchar(256),"
                        "description varchar(256),"
                        "photo varchar(1000),"
                        "type chat_type,"
                        "time_recall timetz NOT NULL DEFAULT '12:00 MSK');")

            cur.execute("CREATE TABLE IF NOT EXISTS Users ("
                        "user_id integer CONSTRAINT users_pkey PRIMARY KEY,"
                        "chat_id integer REFERENCES conversations ON DELETE SET NULL ON UPDATE CASCADE,"
                        "username varchar(32),"
                        "first_name varchar(256),"
                        "last_name varchar(256),"
                        "is_bot boolean,"
                        "language_code varchar(10) DEFAULT 'en');")

            cur.execute("CREATE TABLE IF NOT EXISTS Notes ("
                        "note_id serial UNIQUE,"
                        "chat_id integer REFERENCES conversations ON DELETE CASCADE ON UPDATE CASCADE,"
                        "name varchar(4096) NOT NULL UNIQUE,"
                        "datetime timestamptz(0) NOT NULL,"
                        "CONSTRAINT notes_pkey PRIMARY KEY(chat_id, name));")

            cur.execute(sql.SQL("CREATE OR REPLACE FUNCTION notify_notes() RETURNS trigger AS $$ "
                                "BEGIN "
                                "IF (TG_OP = 'DELETE') THEN "
                                "PERFORM pg_notify(CAST({} AS text), tg_name);"
                                "ELSIF (TG_OP = 'UPDATE') THEN "
                                "PERFORM pg_notify(CAST({} AS text), tg_name);"
                                "ELSIF (TG_OP = 'INSERT') THEN "
                                "PERFORM pg_notify(CAST({} AS text), tg_name);"
                                "END IF;"
                                "RETURN NULL; "
                                "END; "
                                "$$ LANGUAGE plpgsql;").format(sql.Literal(NOTIFY_DELETE_NOTES),
                                                               sql.Literal(NOTIFY_UPDATE_NOTES),
                                                               sql.Literal(NOTIFY_INSERT_NOTES)))

            cur.execute(sql.SQL("DO $$"
                                "BEGIN IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'notify_notes') THEN "
                                "CREATE TRIGGER notify_notes "
                                "AFTER INSERT OR UPDATE OR DELETE ON notes "
                                "FOR EACH STATEMENT "
                                "EXECUTE PROCEDURE notify_notes();"
                                "END IF;"
                                "END; $$;"))

    def update_conversations(self, conversations: dict):
        """
        Method updates a conversation's state in the database.

        :param conversations: a dictionary containing chat_id and conversation state
        """
        # Conversations is dict containing items like: "name_conversation_handler: {chat_id: state}"
        # And it's necessary to swap these values to pass it into the updating data method
        # Now it will be like: "chat_id: {name_conversation_handler: state}"
        _conversations = defaultdict(dict, {})
        for name, id_states in conversations.items():
            for chat_id, state in id_states.items():
                _conversations[chat_id[0]][name] = state
        self.update_data('conversations', _conversations)

    def get_conversations(self) -> dict:
        """
        Method gets conversation states from the database.

        This method returns a dictionary consisting of a tuple and a state of the handler.
        The tuple contains the chat_id. It returns a tuple because of the handler requires it and besides the chat_id,
        the user_id and the message_id may be passed. But now it isn't required and just user_id will be sent.
        This fact may be changed in the ConversationHandler constructor (parameters per_chat, per_user, per_message)

        :return: dictionary
        """
        # It's necessary for the handler that the dictionary will contain the name of the handler like the key
        # Therefore, it must be swapped
        conversations = defaultdict(dict, {})
        for chat_id, names_states in self.get_data('conversations').items():
            for name, state in names_states.items():
                conversations[name][(chat_id,)] = state
        return conversations

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
                    columns = [column[0] for column in cur.fetchall() if column[0] in data[id] or 'id' in column[0]]

                    # Build a list containing all values of this id
                    values = [id]
                    values.extend(data[id].get(column) for column in columns[1:])

                    if not columns:
                        logging.warning("The names of columns from the {} table weren't received".format(table_name))
                        return {}

                    # Build the SQL-string to use "UPSERT" function
                    setting_columns = list(
                        map(lambda x: sql.SQL("{0} = excluded.{0}").format(sql.Identifier(x)), columns[1:]))

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

    def add_entries(self, chat_id: int, entries: set):
        """
        Method adds new entries into the database. The method gets recall time from the other table and set this time
        into the notes table. This datetime will be compared with the date and the time at the moment.

        :param chat_id: the id of the chat
        :param entries: the set that contains tuples containing the name and the date of an entry
        """

        # Get recall time from the chats table for this chat_id
        with self.connection.cursor() as cur:
            query = sql.SQL("SELECT time_recall FROM chats WHERE chat_id = {}").format(sql.Literal(chat_id))
            cur.execute(query)
            time_recall = cur.fetchone()[0]

        for name, entry_date, time in entries:
            with self.connection.cursor() as cur:
                if not time:
                    time = time_recall
                entry_date = dt.datetime.combine(entry_date, time)

                query = sql.SQL("INSERT INTO notes(chat_id, name, datetime) VALUES ({0}, {1}, {2})"
                                "ON CONFLICT (chat_id, name) DO UPDATE SET datetime = excluded.datetime").format(
                    sql.Literal(chat_id), sql.Literal(name), sql.Literal(entry_date))
                cur.execute(query)

    def get_entries(self, start_time: dt.datetime, finish_time: dt.datetime) -> list:
        """
        This method gets all entries from the notes table and returns these values + language_code of a user.
        Method gets entries having the datetime value is during the specific period (from start_time to finish_time).

        :param start_time: the start of the period
        :param finish_time: the end of the period
        :return: the tuple: (chat_id, name, datetime, language_code)
        """
        with self.connection.cursor() as cur:
            query = sql.SQL("SELECT notes.note_id, notes.chat_id, notes.name, notes.datetime, users.language_code "
                            "FROM notes INNER JOIN users ON notes.chat_id = users.chat_id "
                            "WHERE datetime BETWEEN {}::timestamp AND {}::timestamp;").format(
                sql.Literal(start_time), sql.Literal(finish_time))
            cur.execute(query)
            entries = [Entry(entry[0], entry[1], entry[2], entry[3], entry[4]) for entry in cur.fetchall()]
        return entries

    def notify(self, notify):
        """
        This method notifies the database of the event with the name 'notify'.

        :param notify: the name of the channel
        """
        with self.connection.cursor() as cur:
            query = sql.SQL("NOTIFY {};").format(sql.Identifier(notify))
            cur.execute(query)


class Entry:
    def __init__(self, note_id: int, chat_id: int, name: str, entry_date: dt.datetime, language_code: str):
        self.note_id = note_id
        self.chat_id = chat_id
        self.name = name
        self.entry_date = entry_date
        self.language_code = language_code
