import sys
from birthdaybot.configurator import Configurator
from birthdaybot.bot import BirthdayBot
from birthdaybot.db.database import Database

import psycopg2


def main():
    configurator = Configurator(sys.argv[1:])

    try:
        database = Database(configurator.get_dbconfig())
    except KeyError as e:
        print("Error: Undefined parameter {}".format(e), file=sys.stderr)
        exit(-1)

    bot = BirthdayBot(configurator.get_token(), configurator.get_persistence())
    bot.run()


if __name__ == "__main__":
    main()
