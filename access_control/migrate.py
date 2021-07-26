from flask import Flask
from conf import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from db_models import db, Role, UserRoleMap, User
from sqlalchemy_utils import database_exists, create_database

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

            admin_role = Role(name="admin")
            user_role = Role(name="election_official")

            db.session.add(admin_role)
            db.session.add(user_role)
            db.session.commit()

            admin = User(
                jmbg="0000000000000",
                forename="admin",
                surname="admin",
                email="admin@admin.com",
                password="1"
            )

            db.session.add(admin)
            db.session.commit()

            user_role = UserRoleMap(
                user_id=admin.id,
                role_id=admin_role.id
            )

            db.session.add(user_role)
            db.session.commit()

            done = True
    except Exception:
        pass
