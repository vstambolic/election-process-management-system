from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def permission_control(role):
    def inner_role(function):
        @wraps(function)
        def decorator(*arguments, **keyword_arguments):
            verify_jwt_in_request()
            additional_claims = get_jwt()
            if "roles" in additional_claims and role in additional_claims["roles"]:
                return function(*arguments, **keyword_arguments)
            else:
                return jsonify(message = 'Missing Authorization Header'), 401

        return decorator

    return inner_role
