from datetime import timedelta

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token
from psycopg2 import errorcodes

from init import db, bcrypt
from models.user import User, user_schema

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def auth_register():
    try:
        # Get the data from the body of the request
        body_data = request.get_json()
        # Create user instance
        user = User(
            name=body_data.get("name"),
            email=body_data.get("email"),
        )
        # Get password from the request body
        password = body_data.get("password")
        # Check if password exists, if it does, hash it
        if password:
            user.password = bcrypt.generate_password_hash(password).decode(
                "utf-8"
            )
        # Add and commit user to DB
        db.session.add(user)
        db.session.commit()
        # Respond back to client
        return user_schema.dump(user), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Email address is already in use"}, 409
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {
                "error": f"The {err.orig.diag.column_name} is required"
            }, 400


@auth_bp.route("/login", methods=["POST"])
def auth_login():
    # Get the data from the request body
    body_data = request.get_json()
    # Find user with the email address
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    # If user exists and password is correct
    if user and bcrypt.check_password_hash(
        user.password, body_data.get("password")
    ):
        # Create JWT
        token = create_access_token(
            identity=str(user.id), expires_delta=timedelta(days=1)
        )
        # Return the token along with the user info
        return {"email": user.email, "token": token, "is_admin": user.is_admin}
    # Else
    else:
        # Return error
        return {"error": "Invalid email or password"}, 401
