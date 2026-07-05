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
    pianoesami,
)
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import jsonify, request, Blueprint
from app.models import utenti, db, create_inst_id

bp_ufficio = Blueprint(
    "ufficio",
    __name__,
)


def require_role(expected_role):
    claims = get_jwt()
    if claims.get("ruolo") != expected_role:
        return jsonify({"msg": "Accesso non autorizzato"}), 403

# per la query doppia su utenti
studente = aliased(utenti)
docente = aliased(utenti)


@bp_ufficio.route("/app/tutte", methods=["GET"])
@jwt_required()
def tutte_le_app():
    auth = require_role("ufficio")
    if auth:
        return auth

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
                "ida": app.ida,
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


@bp_ufficio.route("/pratiche/<id_pratica>", methods=["GET"])
@jwt_required()
def dettaglio_pratica(id_pratica):
    auth = require_role("ufficio")
    if auth:
        return auth

    query = (
        select(applicazione, institution, pianoesami, studente, docente)
        .outerjoin(institution, applicazione.idin == institution.idin)
        .outerjoin(pianoesami, applicazione.ida == pianoesami.ida)
        .outerjoin(studente, applicazione.username_studente == studente.username)
        .outerjoin(docente, applicazione.username_docente == docente.username)
        .where(applicazione.ida == id_pratica)
    )

    risultati = db.session.execute(query).all()

    if not risultati:
        return jsonify({"error": "Pratica non trovata"}), 404

    app = risultati[0][0]
    ist = risultati[0][1]
    stud = risultati[0][3]
    doc = risultati[0][4]

    # 3. Estrai l'elenco di TUTTI gli esami da TUTTE le righe
    # riga[2] corrisponde a 'pianoesami' nel tuo select(...) originale
    tutti_gli_esami = [row[2] for row in risultati]

    dettaglio = {
        "ida": app.ida,
        "stato": app.stato,
        "periodo": app.periodo_previsto,
        "istituto": {
            "nome": ist.nome if ist else "Nessun istituto",
            "paese": ist.paese if ist else "-",
        },
        "studente": {
            "nome": stud.nome if stud else "Sconosciuto",
            "cognome": stud.cognome if stud else "",
            "username": stud.username if stud else "",
        },
        "docente": {
            "nome": doc.nome if doc else "Nessun",
            "cognome": doc.cognome if doc else "docente",
        },
        "pianoesami": [
            {
                
                "id": e.idpe,
                "codice_estero": e.codiceinsegnamentoestero,
                "titolo_estero": e.titoloinsegnamentoestero,
                "crediti_estero": e.creditiinsegnamentoestero,
                "codice_cafoscari": e.codiceinsegnamentocafoscari,
                "titolo_cafoscari": e.titoloinsegnamentocafoscari,
                "crediti_cafoscari": e.creditiinsegnamentocafoscari,
                "voto_ottenuto": getattr(e, "voto_ottenuto", None),
                "data_superamento": getattr(e, "data_superamento", None),
                "stato_riconoscimento": getattr(e, "stato_riconoscimento", "in_attesa"),
            }
            for e in tutti_gli_esami if e is not None
        ],
    }
    print(dettaglio)
    return jsonify(dettaglio), 200


@bp_ufficio.route("/pratiche/<string:id_pratica>/stato", methods=["PUT"])
@jwt_required()
def verifica_app(id_pratica):
    auth = require_role("ufficio")
    if auth:
        return auth

    dati = request.json
    statoAgg = dati["stato"]

    if not statoAgg:
        return jsonify({"msg": "campo mancante"}), 400
    
    query = select(applicazione).where(applicazione.ida == id_pratica)
    app = db.session.execute(query).scalars().first()

    if not app:
        return jsonify({"msg": "applicazione non trovata"}), 400
    
    if statoAgg == "in corso":

        if not app.idla:
            return jsonify({"msg": "⛔ Impossibile passare 'in corso': Nessun Learning Agreement collegato alla pratica."}), 403

        query_la = select(learningagreement).where(learningagreement.idla == app.idla)
        la = db.session.execute(query_la).scalars().first()

        if not la or str(la.accettato).lower() not in ['sì', 'si', 'approvato']: 
            return jsonify({"msg": "⛔ Impossibile passare 'in corso': Il Docente non ha ancora approvato il Learning Agreement!"}), 403

    if statoAgg in ["completato", "chiusa", "chiuso"]:
        if not app.transcriptofrecords or str(app.transcriptofrecords).lower() != "caricato":
            return jsonify({"msg": "⛔ Impossibile chiudere la pratica: Il Transcript of Records non è ancora stato caricato!"}), 403


    try:
        app.stato = statoAgg
        db.session.commit()
        return jsonify({"msg": "Stato aggiornato con successo!", "nuovo_stato": app.stato}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Errore database: {str(e)}"}), 500



#inutilizzate
@bp_ufficio.route("/app/da-approvare", methods=["GET"])
@jwt_required()
def app_da_verificare():
    auth = require_role("ufficio")
    if auth:
        return auth

    query = select(applicazione).where(applicazione.stato == "pre-partenza")

    pratiche = db.session.execute(query).scalars().all()

    return jsonify([p.to_dict() for p in pratiche])


@bp_ufficio.route("/app/da-chiudere", methods=["GET"])
@jwt_required()
def app_da_chiudere():
    auth = require_role("ufficio")
    if auth:
        return auth

    query = select(applicazione).where(applicazione.stato == "viaggioCompletato")

    chiusure = db.session.execute(query).scalars().all()

    return jsonify([c.to_dict() for c in chiusure])


@bp_ufficio.route("/istituti", methods=["POST"])
@jwt_required()
def aggiungi_istituto():
    auth = require_role("ufficio")
    if auth:
        return auth

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
