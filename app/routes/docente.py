import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, select

from app.models import applicazione, studente, learningagreement, docentireferenti
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request, Blueprint
from app.models import utenti, db

bp_docente = Blueprint(
    "docente",
    __name__,
)


@bp_docente.route("/studenti", methods=["GET"])
@jwt_required()
def get_studenti():
    docente_id = get_jwt_identity()
    studenti = applicazione.query.filter_by(username_docente=docente_id).all()
    return jsonify([s.to_dict() for s in studenti]), 200


@bp_docente.route("studenti/<string:username>/applicazione", methods=["GET"])
@jwt_required()
def get_applicazione(username):
    docente_id = get_jwt_identity()
    application = select(applicazione).where(
        applicazione.username_docente == docente_id,
        applicazione.username_studente == username,
    )
    app = db.session.execute(application).scalars().first()

    if not app:
        return jsonify({"msg": "Applicazione non trovata per questo studente"}), 404

    return jsonify(app.to_dict()), 200


@bp_docente.route(
    "studenti/<username>/applicazione/<ida>/learning_agreement", methods=["GET"]
)
@jwt_required()
def get_learning_agreement(ida, username):
    docente_id = get_jwt_identity()
    learningA = select(applicazione).where(
        applicazione.ida == ida, applicazione.username_docente == docente_id
    )
    learningA = sq.select(applicazione.c.idla).where(
        applicazione.ida == ida, applicazione.username_docente == docente_id
    )
    la = sq.select(learningagreement).where(
        learningagreement.c.idla == learningA.c.idla,
    )
    return jsonify(la.to_dict())
