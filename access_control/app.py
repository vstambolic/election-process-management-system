# import time

from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, \
    get_jwt
from sqlalchemy import and_

from conf import Configuration
from data_validator import JMBGValidator, EmailValidator, PasswordValidator
from utils.permission_control import permission_control
from db_models import db, User, Role, UserRoleMap

app = Flask(__name__)
app.config.from_object(Configuration)

jwt = JWTManager(app)


def create_missing_fields_message(missing_fields):
    return ['Field ' + field + ' is missing.' for field in missing_fields]


def format_missing_field_message(field):
    return 'Field ' + field + ' is missing.'


@app.route("/register", methods=["POST"])
def register():
    if request.json is None:
        missing_fields = ['jmbg', 'forename', 'surname', 'email', 'password']
        missing_fields = create_missing_fields_message(missing_fields)
        return jsonify(message=missing_fields), 400

    # Check for missing fields

    # missing_fields = []

    jmbg = request.json.get('jmbg', '')
    if len(jmbg) == 0:
        return jsonify(message=format_missing_field_message('jmbg')), 400
        # missing_fields.append('jmbg')

    forename = request.json.get('forename', '')
    if len(forename) == 0:
        return jsonify(message=format_missing_field_message('forename')), 400
        # missing_fields.append('forename')

    surname = request.json.get('surname', '')
    if len(surname) == 0:
        return jsonify(message=format_missing_field_message('surname')), 400
        # missing_fields.append('surname')

    email = request.json.get('email', '')
    if len(email) == 0:
        return jsonify(message=format_missing_field_message('email')), 400
        # missing_fields.append('email')

    password = request.json.get('password', '')
    if len(password) == 0:
        return jsonify(message=format_missing_field_message('password')), 400
        # missing_fields.append('password')

    # if len(missing_fields) != 0:
    #     missing_fields = create_missing_fields_message(missing_fields)
    #     return jsonify(message=missing_fields), 400

    jmbg_validator = JMBGValidator(jmbg)
    if not jmbg_validator.is_valid():
        return jsonify(message="Invalid jmbg."), 400

    email_validator = EmailValidator(email)
    if not email_validator.is_valid():
        return jsonify(message="Invalid email."), 400

    if not PasswordValidator(password).is_valid():
        return jsonify(message="Invalid password."), 400

    if not email_validator.is_unique():
        return jsonify(message="Email already exists."), 400

    if not jmbg_validator.is_unique():
        return jsonify(message="JMBG already exists."), 400

    user = User(jmbg=jmbg, forename=forename, surname=surname, email=email, password=password)

    db.session.add(user)
    db.session.commit()

    role_id = Role.query.filter(Role.name == "election_official").first().id
    user_role = UserRoleMap(user_id=user.id, role_id=role_id)

    db.session.add(user_role)
    db.session.commit()

    return Response(status=200)


@app.route("/login", methods=["POST"])
def login():
    if request.json is None:
        missing_fields = ['email', 'password']
        missing_fields = create_missing_fields_message(missing_fields)
        return jsonify(message=missing_fields), 400

    # Check for missing fields
    # missing_fields = []

    email = request.json.get("email", "")
    if len(email) == 0:
        return jsonify(message=format_missing_field_message('email')), 400
        # missing_fields.append('email')

    password = request.json.get("password", "")
    if len(password) == 0:
        return jsonify(message=format_missing_field_message('password')), 400
        # missing_fields.append('password')

    # if len(missing_fields) != 0:
    #     missing_fields = create_missing_fields_message(missing_fields)
    #     return jsonify(message=missing_fields), 400

    if not EmailValidator(email).is_valid():
        return jsonify(message="Invalid email."), 400

    user = User.query\
        .filter(and_(User.email == email, User.password == password))\
        .first()
    if user is None:
        return jsonify(message="Invalid credentials."), 400

    additional_claims = {
        "jmbg": user.jmbg,
        "forename": user.forename,
        "surname": user.surname,
        "email": user.email,
        # "password": user.password,
        "roles": [role.name for role in user.roles]
    }

    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)
    # time.sleep(1)

    return jsonify(accessToken=access_token, refreshToken=refresh_token), 200


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refresh_claims = get_jwt()

    additional_claims = {
        "jmbg": refresh_claims["jmbg"],
        "forename": refresh_claims["forename"],
        "surname": refresh_claims["surname"],
        "email": refresh_claims["email"],
        # "password": refresh_claims["password"],
        "roles": refresh_claims["roles"]
    }

    access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    # time.sleep(1)
    return jsonify(accessToken=access_token), 200


@app.route("/delete", methods=["POST"])
@permission_control('admin')
def delete():
    if request.json is None:
        return jsonify(message='Field email is missing.'), 400

    email = request.json.get('email', '')

    if len(email) == 0:
        return jsonify(message='Field email is missing.'), 400

    if not EmailValidator(email).is_valid():
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(User.email == email).first()

    if user is None:
        return jsonify(message="Unknown user."), 400

    db.session.delete(user)
    db.session.commit()

    return Response(status=200)


@app.route("/", methods=["GET"])
def index():
    return "Hello world!"


if __name__ == "__main__":
    # done = False
    # while not done:
    #     try:
    #         ...
    #         done = True
    #     except Exception:
    #         pass
    db.init_app(app)
    app.run(debug=True, host="0.0.0.0", port=5001)
