import sys
from birthdaybot.configurator import Configurator
from birthdaybot.bot import BirthdayBot


def main():
    configurator = Configurator(sys.argv[1:])
    bot = BirthdayBot(configurator.get_token())
    bot.run()


if __name__ == "__main__":
    main()