from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class UserRoleMap(db.Model):
    __tablename__ = "user_role_map"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    jmbg = db.Column(db.String(13), nullable=False, unique=True)
    forename = db.Column(db.String(256), nullable=False)
    surname = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)

    roles = db.relationship("Role", secondary=UserRoleMap.__table__, back_populates="users")


class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True)

    users = db.relationship("User", secondary=UserRoleMap.__table__, back_populates="roles")