import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, select

from app.models import applicazione, studente, learningagreement, docentireferenti, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request, Blueprint, redirect

bp_studente = Blueprint(
    "studente",
    __name__,
)


@bp_studente.route("/my_applicazione", methods=["GET"])
@jwt_required()
def get_my_app():
    studente_id = get_jwt_identity()

    query = select(applicazione).where(applicazione.username_studente == studente_id)

    app = db.session.execute(query).first()
    if not app:
        return jsonify({"msg": "lo studente non possiede un'applicazione, crearne una"})

    # NON SO SE ABBIA SENSO
    match app.stato:
        case "creato":
            return
        case "in attesa":
            return
        case "pre-partenza":
            return
        case "in corso":
            return
        case "completato":
            return
        case "annullato":
            return
        case "viaggioCompletato":
            return
    return jsonify([a.to_dict() for a in app])


@bp_studente.route("/create_applicazione", methods=["PATCH"])
@jwt_required()
def create_myapp():
    studente_id = get_jwt_identity()


