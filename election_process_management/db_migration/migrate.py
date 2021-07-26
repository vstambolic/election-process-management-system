from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy_utils import database_exists, create_database

from conf import Configuration
from db_models import db

app = Flask(__name__)
app.config.from_object(Configuration)

Migrate(app, db)


done = False

while not done:
    try:
        if not database_exists(Configuration.SQLALCHEMY_DATABASE_URI):
            create_database(Configuration.SQLALCHEMY_DATABASE_URI)

        db.init_app(app)

        with app.app_context() as context:
            init()
            migrate(message="Production migration")
            upgrade()

            done = True

    except Exception:
        pass
