import pymysql


class Database:
    def __init__(self):
        self.host = 'db.seopia.online'
        self.user = 'seopia'
        self.password = ''
        self.database = 'crawling'

    def connect(self):
        print("DB 연결")
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )


db = Database()
