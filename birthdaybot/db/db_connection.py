"""
This module implements the database connection.
"""
import psycopg2
import sys
from abc import ABC


class DatabaseConnection(ABC):
    def __init__(self, json_obj):
        self._name = json_obj["PG_NAME"]
        self._user = json_obj["PG_USER"]
        self._password = json_obj["PG_PSWD"]
        self._host = json_obj["PG_HOST"]
        self._port = json_obj["PG_PORT"]

        self.connection = self._connect()

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
