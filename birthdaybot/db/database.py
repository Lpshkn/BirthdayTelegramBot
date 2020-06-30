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

    def create_tables(self):
        with self.connection.cursor() as cur:
            self.connection.autocommit = True

            cur.execute("CREATE TABLE IF NOT EXISTS Chats ("
                        "chat_id integer CONSTRAINT chats_pkey PRIMARY KEY,"
                        "conversation_state varchar(64) NOT NULL);")

            cur.execute("CREATE TABLE IF NOT EXISTS Users ("
                        "user_id integer CONSTRAINT users_pkey PRIMARY KEY,"
                        "chat_id integer REFERENCES Chats ON DELETE SET NULL ON UPDATE CASCADE,"
                        "username varchar(32) NOT NULL UNIQUE);")

            cur.execute("CREATE TABLE IF NOT EXISTS Notes ("
                        "note_id integer CONSTRAINT notes_pkey PRIMARY KEY,"
                        "chat_id integer REFERENCES Chats ON DELETE CASCADE ON UPDATE CASCADE,"
                        "datetime timestamp(0) NOT NULL UNIQUE);")
