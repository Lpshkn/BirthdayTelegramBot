"""
This module implements the class that sets up notifies and implements listening to a database.
The listening is implemented in a separate process.
"""
import psycopg2
import psycopg2.extensions
import logging
from select import select
from psycopg2 import sql
from multiprocessing import Process
from birthdaybot.db.db_connection import DatabaseConnection


class DatabaseNotify(DatabaseConnection):
    TIMEOUT = 3

    def __init__(self, json_obj):
        super().__init__(json_obj)

        self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.__listening = False

    def __listen(self, callable_function, *args):
        if self.__listening:
            logging.warning("You're trying to run listening to the database, but it is already listening")
        else:
            self.__listening = True
            while self.__listening:
                if select([self.connection], [], [], self.TIMEOUT) != ([], [], []):
                    self.connection.poll()
                    while self.connection.notifies:
                        pid, notify = self.connection.notifies.pop()

                        # Call the callable function and pass it the dictionary of arguments
                        callable_function(args[0])

    def listen(self, notify):
        """Subscribe to a PostgreSQL NOTIFY"""
        with self.connection.cursor() as cur:
            query = sql.SQL("LISTEN {};").format(sql.Identifier(notify))
            cur.execute(query)

    def remove(self, notify):
        """Unsubscribe a PostgreSQL LISTEN"""
        with self.connection.cursor() as cur:
            query = sql.SQL("UNLISTEN {};").format(sql.Identifier(notify))
            cur.execute(query)

    def stop(self):
        """Call to stop the listen thread"""
        self.__listening = False

    def run(self, callable_function, **kwargs):
        """
        Start listening in a separate process and return that as an instance

        :param callable_function: the function that will be called when a notify will be occurred
        :param kwargs: a dictionary containing arguments and its values
        """
        proc = Process(target=self.__listen, args=(callable_function, kwargs))
        proc.start()
        return proc
