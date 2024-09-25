import pymysql as sql
from dotenv import load_dotenv
import os

load_dotenv()


class DB:
    def __init__(self):
        self.conn = sql.connect(host=os.getenv("HOST"), user=os.getenv("USER"), password=os.getenv("PASSWORD"), database=os.getenv("DATABASE"), port=int(os.getenv("PORT")), charset='utf8')
        self.cursor = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def execute(self, sql):
        self.cursor.execute(sql)

    def result(self):
        return self.cursor.fetchall()

    def rollback(self):
        self.conn.rollback()