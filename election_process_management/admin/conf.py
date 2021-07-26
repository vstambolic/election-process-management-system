from datetime import timedelta
import os

DB_URI = os.environ["DB_URI"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_URI}/{DB_NAME}"
    # REDIS_HOST = "localhost"
    # REDIS_VOTE_CHANNEL = "votes_channel"
    JWT_SECRET_KEY = "secret"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JSON_SORT_KEYS = False
