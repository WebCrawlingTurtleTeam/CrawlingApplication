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
            query = "DELETE FROM movies"
            cursor.execute(query)
            for movie in movies:
                query = "INSERT INTO movies (movie_name, update_at) VALUES (%s, NOW())"
                cursor.execute(query, (movie,))
        self.conn.commit()

    # name으로 movie에서 movie테이블의 movie_name이 name인 movie_code와
    # review 테이블의 movie_code가 일치하는 것을 return한다.
    def get_review(self, movie_name, platform):
        with self.conn.cursor() as cursor:
            query = "SELECT r.review_content, r.review_update_at FROM reviews r JOIN movies m ON m.movie_code = r.movie_code WHERE m.movie_name = %s AND r.platform = %s"
            cursor.execute(query, (movie_name, platform,))
            return cursor.fetchall()

    def insert_review(self, reviews, movie_name, platform):
        with self.conn.cursor() as cursor:
            query = "DELETE FROM reviews WHERE platform = %s"
            cursor.execute(query, (platform,))

            query = "SELECT movie_code FROM movies WHERE movie_name = %s"
            cursor.execute(query, (movie_name,))
            movie_code = cursor.fetchall()[0][0]
            for review in reviews:
                query = "INSERT INTO reviews (movie_code, review_content,review_update_at,platform) VALUES (%s, %s, NOW(),%s)"
                cursor.execute(query, (movie_code, review, platform,))
            self.conn.commit()
    def close_connection(self):
        self.conn.close()



