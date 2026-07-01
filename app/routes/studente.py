import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, select
from app.models import (
    applicazione,
    institution,
    studente,
    learningagreement,
    docentireferenti,
    db,
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request, Blueprint, redirect
from app.models import pianoesami, applicazione, create_id

bp_studente = Blueprint(
    "studente",
    __name__,
)


@bp_studente.route("/pratiche", methods=["GET"])
@jwt_required()
def get_my_app():
    studente_id = get_jwt_identity()
    query = select(applicazione).where(applicazione.username_studente == studente_id)
    app = (
        db.session.execute(query).scalars().all()
    )  # messo all al posto di first, dato che angular si aspetta una lista

    if not app:
        return jsonify([]), 200
    pratiche_json = [pratica.to_dict() for pratica in app]
    return jsonify(pratiche_json), 200


@bp_studente.route("/pratiche", methods=["POST"])
@jwt_required()
def create_myapp():
    studente_id = get_jwt_identity()
    dati = request.json
    nuovo_ida = create_id(db.session, applicazione)
    anno_acc = dati["anno_accademico"]
    istituto_id = dati["istituto_id"]
    periodo = dati["periodo"]
    docente = dati["docente_id"]

    app = applicazione(
        ida=nuovo_ida,
        stato="creato",
        esami=False,
        transcriptofrecords="null",
        idin=istituto_id,
        username_studente=studente_id,
        username_docente=docente,
        anno_accademico=anno_acc,
        periodo_previsto=periodo,
    )

    db.session.add(app)
    db.session.flush()

    nuovi_esami = [
        pianoesami(
            ida=nuovo_ida,
            applicazione_id=dati["applicazione_id"],
            codice_estero=e["codice_estero"],
            titolo_estero=e["titolo_estero"],
            crediti_estero=e["crediti_estero"],
            codice_cafoscari=e["codice_cafoscari"],
            titolo_cafoscari=e["titolo_cafoscari"],
            crediti_cafoscari=e["crediti_cafoscari"],
        )
        for e in dati["mapping_esami"]  
    ]

    db.session.add_all(nuovi_esami)
    db.session.commit()
    return jsonify({"ida": app.ida, "id": app.ida}), 201


@bp_studente.route("/istituti", methods=["GET"])
@jwt_required()
def get_my_institution():

    query = select(institution)
    institution_db = db.session.execute(query).scalars().all()
    return jsonify([istituti.to_dict() for istituti in institution_db]), 200


@bp_studente.route("/docente", methods=["GET"])
@jwt_required()
def get_my_docente():

    query = select(docentireferenti)
    docentireferenti_db = db.session.execute(query).scalars().all()
    return jsonify([docenti.to_dict() for docenti in docentireferenti_db]), 200
