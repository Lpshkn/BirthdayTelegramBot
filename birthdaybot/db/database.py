import psycopg2
import birthdaybot.configurator as cfg
from os.path import join


class Database:
    def __init__(self, json_obj):
        self.name = json_obj["PG_NAME"]
        self.user = json_obj["PG_USER"]
        self.password = json_obj["PG_PSWD"]
        self.host = json_obj["PG_HOST"]
        self.port = json_obj["PG_PORT"]
