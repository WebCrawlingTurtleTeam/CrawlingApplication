from database import db


class CRUD:
    def __init__(self):
        self.conn = db.connect()

    def get_movies(self):
        with self.conn.cursor() as cursor:
            query = "SELECT movie_name, update_at FROM movies"
            cursor.execute(query)
        return cursor.fetchall()

    def insert_movie(self, movies):
        with self.conn.cursor() as cursor:
            for movie in movies:
                query = "INSERT INTO movies (movie_name, update_at) VALUES (%s, NOW())"
                cursor.execute(query, (movie,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()



