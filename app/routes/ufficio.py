import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, select

from app.models import applicazione, studente, learningagreement, docentireferenti
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request, Blueprint

bp_ufficio = Blueprint(
    "ufficio",
    __name__,
)


@bp_ufficio.route("/app/tutte", methods = ["GET"])
@jwt_required()
def tutte_le_app():

    query = select(applicazione)

    pratiche = sq.session.execute(query).scalars().all()

    return jsonify([p.to_dict() for p in pratiche])


@bp_ufficio.route("/app/da-approvare", methods = ["GET"])
@jwt_required()
def app_da_verificare():

    query = select(applicazione).where(applicazione.stato == 'LA_Approvato')

    pratiche = sq.session.execute(query).scalars().all()

    return jsonify([p.to_dict() for p in pratiche])


@bp_ufficio.route("/app/da-chiudere", methods = ["GET"])
@jwt_required()
def app_da_chiudere():

    query = select(applicazione).where(applicazione.stato == 'ric_completato')

    chiusure = sq.session.execute(query).scalars().all()

    return jsonify([c.to_dict() for c in chiusure])
    