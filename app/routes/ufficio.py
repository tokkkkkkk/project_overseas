import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, select

from app.models import applicazione, studente, learningagreement, docentireferenti
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request, Blueprint
from app.models import utenti, db

bp_ufficio = Blueprint(
    "ufficio",
    __name__,
)


@bp_ufficio.route("/app/tutte", methods = ["GET"])
@jwt_required()
def tutte_le_app():

    query = select(applicazione)

    pratiche = db.session.execute(query).scalars().all()

    return jsonify([p.to_dict() for p in pratiche])


@bp_ufficio.route("/app/da-approvare", methods = ["GET"])
@jwt_required()
def app_da_verificare():

    query = select(applicazione).where(applicazione.stato == 'pre-partenza')

    pratiche = db.session.execute(query).scalars().all()

    return jsonify([p.to_dict() for p in pratiche])

@bp_ufficio.route("/app/<string:ida>/approvazione", methods = ["PATCH"])
@jwt_required()
def verifica_app(ida):
    dati = request.json
    statoAgg = dati.get("stato")

    if not statoAgg:
        return jsonify({"msg": "campo stato mancante"}), 400
    
    query = select(applicazione).where(applicazione.ida == ida)
    app = db.session.execute(query).scalars().first()
    if not app:
        return jsonify({"msg": "applicazione non trovata"}), 404
    
    if app.stato != "pre-partenza":
        return jsonify({"msg": "stato non valido per l'operazione"})
    
    app.stato = statoAgg    
    db.session.commit()

    return jsonify({"msg": "app aggiornata"}), 200


@bp_ufficio.route("/app/da-chiudere", methods = ["GET"])
@jwt_required()
def app_da_chiudere():

    query = select(applicazione).where(applicazione.stato == 'viaggioCompletato')

    chiusure = db.session.execute(query).scalars().all()

    return jsonify([c.to_dict() for c in chiusure])

@bp_ufficio.route("/app/<string:ida>/chiusura", methods = ["PATCH"])
@jwt_required()
def chiusura_app(ida):
    dati = request.json
    statoAgg = dati.get("stato")

    if not statoAgg:
        return jsonify({"msg": "campo stato mancante"}), 400
    
    query = select(applicazione).where(applicazione.ida == ida)
    app = db.session.execute(query).scalars().first()
    if not app:
        return jsonify({"msg": "applicazione non trovata"}), 404
    
    if app.stato != "viaggioCompletato":
        return jsonify({"msg": "stato non valido per l'operazione"})
    
    app.stato = statoAgg    
    db.session.commit()

    return jsonify({"msg": "app aggiornata"}), 200
    