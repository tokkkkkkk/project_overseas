import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, aliased
from sqlalchemy import Integer, String, select

from app.models import (
    applicazione,
    studente,
    learningagreement,
    docentireferenti,
    institution,
    utenti,
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request, Blueprint
from app.models import utenti, db, create_inst_id

bp_ufficio = Blueprint(
    "ufficio",
    __name__,
)

# per la query doppia su utenti
studente = aliased(utenti)
docente = aliased(utenti)


@bp_ufficio.route("/app/tutte", methods=["GET"])
@jwt_required()
def tutte_le_app():

    query = (
        select(applicazione, institution, studente, docente)
        .join(institution, applicazione.idin == institution.idin)
        .join(studente, applicazione.username_studente == studente.username)
        .join(docente, applicazione.username_docente == docente.username)
    )

    pratiche = db.session.execute(query).all()

    lista_pratiche = []
    for app, ist, stud, doc in pratiche:
        lista_pratiche.append(
            {
                "id": app.ida,
                # strutture di invio dati per restituirli uguali a come sono richiesti nel file del frontend
                "studente": {
                    "nome": stud.nome,
                    "cognome": stud.cognome,
                },
                "istituto": {
                    "nome": ist.nome,
                    "paese": ist.paese,
                },
                "periodo": app.periodo_previsto,
                "stato": app.stato,
                "docente": {
                    "nome": doc.nome,
                    "cognome": doc.cognome,
                },
            }
        )

    return jsonify(lista_pratiche), 200


@bp_ufficio.route("/app/<string:id_pratica>", methods=["GET"])
@jwt_required()
def dettaglio_pratica(id_pratica):

    query = (
        select(applicazione, institution, studente, docente)
        .join(institution, applicazione.idin == institution.idin)
        .join(studente, applicazione.username_studente == studente.username)
        .join(docente, applicazione.username_docente == docente.username)
        .where(applicazione.ida == id_pratica)
    )

    risultato = db.session.execute(query).first()

    if not risultato:
        return jsonify({"error": "Pratica non trovata"}), 404

    app, ist, stud, doc = risultato

    dettaglio = {
        "id": app.ida,
        "stato": app.stato,
        "periodo": app.periodo_previsto,
        "istituto": {
            "nome": ist.nome,
            "paese": ist.paese,
        },
        "studente": {
            "nome": stud.nome,
            "cognome": stud.cognome,
            "username": stud.username,
        },
        "docente": {
            "nome": doc.nome,
            "cognome": doc.cognome,
        },
    }

    return jsonify(dettaglio), 200


@bp_ufficio.route("/app/da-approvare", methods=["GET"])
@jwt_required()
def app_da_verificare():

    query = select(applicazione).where(applicazione.stato == "pre-partenza")

    pratiche = db.session.execute(query).scalars().all()

    return jsonify([p.to_dict() for p in pratiche])


@bp_ufficio.route("/app/<string:ida>/approvazione", methods=["PATCH"])
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


@bp_ufficio.route("/app/da-chiudere", methods=["GET"])
@jwt_required()
def app_da_chiudere():

    query = select(applicazione).where(applicazione.stato == "viaggioCompletato")

    chiusure = db.session.execute(query).scalars().all()

    return jsonify([c.to_dict() for c in chiusure])


@bp_ufficio.route("/app/<string:ida>/chiusura", methods=["PATCH"])
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


@bp_ufficio.route("/istituti", methods=["POST"])
@jwt_required()
def aggiungi_istituto():
    username = get_jwt_identity()
    dati = request.json

    n_idin = create_inst_id(db.session, institution)
    n_nome = dati["nome"]
    n_paese = dati["paese"]
    n_citta = dati["citta"]
    n_username_ufficio = username

    istituto = institution(
        idin=n_idin,
        nome=n_nome,
        paese=n_paese,
        citta=n_citta,
        username_ufficio=n_username_ufficio,
    )

    db.session.add(istituto)
    db.session.flush()

    db.session.commit()
    return jsonify({"message": "Istituto aggiunto con successo!"}), 201
