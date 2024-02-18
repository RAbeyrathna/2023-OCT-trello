from datetime import date
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.card import Card, cards_schema, card_schema

cards_bp = Blueprint("cards", __name__, url_prefix="/cards")


@cards_bp.route("/")
def get_all_cards():
    stmt = db.select(Card).order_by(Card.date.desc())
    cards = db.session.scalars(stmt)
    return cards_schema.dump(cards)


@cards_bp.route("/<int:card_id>")
def get_one_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        return card_schema.dump(card)
    else:
        return {"error": f"Card with id {card_id} not found"}, 404


@cards_bp.route("/", methods=["POST"])
@jwt_required()
def create_card():
    body_data = request.get_json()
    # Create a new card model instance
    card = Card(
        title=body_data.get("title"),
        description=body_data.get("description"),
        date=date.today(),
        status=body_data.get("status"),
        priority=body_data.get("priority"),
        user_id=get_jwt_identity(),
    )
    # Add to sesssion and commit
    db.session.add(card)
    db.session.commit()
    # Return created card
    return card_schema.dump(card), 201


@cards_bp.route("/<int:card_id>", methods=["DELETE"])
def delete_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        db.session.delete(card)
        db.session.commit()
        return {"message": f"Card '{card.title}' been deleted successfully"}
    else:
        return {"error": f"Card with id {card_id} not found"}, 404


@cards_bp.route("/<int:card_id>", methods=["PUT", "PATCH"])
def update_card(card_id):
    body_data = request.get_json()
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        card.title = body_data.get("title") or card.title
        card.description = body_data.get("description") or card.description
        card.status = body_data.get("status") or card.status
        card.priority = body_data.get("priority") or card.priority
        db.session.commit()
        return card_schema.dump(card)
    else:
        return {"error": f"Card with id {card_id} not found"}, 404
