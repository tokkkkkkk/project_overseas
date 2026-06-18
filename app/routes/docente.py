import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

from app.models import applicazione, studente, learningagreement, docentireferenti
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request


@docentireferenti.route("/studenti", methods=["GET"])
@jwt_required()
def get_studenti():
    docente_id = get_jwt_identity()
    studenti = sq.select(docente_id=docente_id)
    return jsonify([s.to_dict() for s in studenti])


@docentireferenti.route("studenti/<username>/applicazione", methods=["GET"])
def get_applicazione():
    docente_id = get_jwt_identity()
    application = sq.select(applicazione).where(
        docente_id == applicazione.c.username_docente
    )
    return jsonify(application.to_dict())


@docentireferenti.route(
    "studenti/<username>/applicazione/<ida>/learning_agreement", methods=["GET"]
)
def get_learning_agreement(ida, username):
    docente_id = get_jwt_identity()
    learningA = sq.select(applicazione.c.idla).where(applicazione.c.ida == ida, applicazione.c.username_docente==docente_id)
    la = sq.select(learningagreement).where(learningagreement.c.idla == learningA.c.idla, 
    )
    return jsonify(la.to_dict())


# @docentireferenti.route()