from datetime import timedelta
import os

REDIS_URI = os.environ["REDIS_URI"]


class Configuration:
    REDIS_HOST = REDIS_URI # "localhost"
    REDIS_VOTE_CHANNEL = "votes_channel"
    JWT_SECRET_KEY = "secret"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JSON_SORT_KEYS = False

