from init import db, ma
from marshmallow import fields


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    cards = db.relationship(
        "Card", back_populates="user", cascade="all, delete"
    )


class UserSchema(ma.Schema):

    cards = fields.List(fields.Nested("CardSchema", exclude=["user"]))

    class Meta:
        fields = ("id", "name", "email", "password", "is_admin", "cards")


# Deserializes data retrieved from the database
user_schema = UserSchema(exclude=["password"])  # {}
users_schema = UserSchema(many=True, exclude=["password"])  # [{}, {}, {}]
