from marshmallow import fields
from init import db, ma


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    title = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"), nullable=False)

    user = db.relationship("User", back_populates="comments")
    card = db.relationship("Card", back_populates="comments")


class CommentSchema(ma.Schema):

    user = fields.Nested("UserSchema", only=["name", "email"])
    card = fields.Nested("CardSchema", exclude=["comments"])

    class Meta:
        field = ("id", "message", "user", "card")


comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
