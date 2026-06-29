import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, select

from app.models import applicazione, studente, learningagreement, docentireferenti
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request, Blueprint, send_file
from app.models import utenti, db
import os

CARTELLA_UPLOADS = "uploads"

bp_docente = Blueprint(
    "docente",
    __name__,
)


@bp_docente.route("/studenti", methods=["GET"])
@jwt_required()
def get_studenti():
    docente_id = get_jwt_identity()
    studenti = select(applicazione).where(applicazione.username_docente==docente_id)
    stud = db.session.execute(studenti).scalar()

    return jsonify(stud.to_dict()), 200
    #return jsonify([s.to_dict() for s in stud]), 200


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
def get_learning_agreement(ida):
    docente_id = get_jwt_identity()

    learningA = select(applicazione).where(
        applicazione.ida == ida, applicazione.username_docente == docente_id
    )
    learning_A = db.session.execute(learningA).scalars().first()
    if not learning_A:
        return jsonify({"msg": "applicazione non trovata"}), 404
    
    la = select(learningagreement).where(
        learningagreement.idla == learning_A.idla
    )
    la_ex = db.session.execute(la).scalars().first()
    if not la_ex:
        return jsonify({"msg": "learning agreement non presente"}), 404
    
    percorso = os.path.join(CARTELLA_UPLOADS, la_ex.percorso_file)

    if not percorso.is_file():
        return jsonify({"msg:" "file non trovato"})
    
    return send_file(percorso)
