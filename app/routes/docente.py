import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, select
from datetime import date

from app.models import (
    applicazione,
    pianoesami,
    studente,
    learningagreement,
    docentireferenti,
    institution,
)
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import jsonify, request, Blueprint, send_file, send_from_directory
from app.models import utenti, db
import os

CARTELLA_UPLOADS = os.path.join(os.getcwd(), "app", "static", "uploads")


def require_role(expected_role):
    claims = get_jwt()
    if claims.get("ruolo") != expected_role:
        return jsonify({"msg": "Accesso non autorizzato"}), 403


bp_docente = Blueprint(
    "docente",
    __name__,
)


@bp_docente.route("/studenti", methods=["GET"])
@jwt_required()
def get_studenti():
    auth = require_role("docente")
    if auth:
        return auth

    docente_id = get_jwt_identity()
    studenti = select(applicazione).where(applicazione.username_docente == docente_id)
    stud = db.session.execute(studenti).scalars().all()

    if not stud:
        return jsonify([]), 200

    return jsonify([s.to_dict() for s in stud]), 200
    # return jsonify([s.to_dict() for s in stud]), 200


@bp_docente.route("/studenti/<string:username>/applicazione", methods=["GET"])
@jwt_required()
def get_applicazione(username):
    auth = require_role("docente")
    if auth:
        return auth

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
    "/studenti/<username>/applicazione/<ida>/learning_agreement", methods=["GET"]
)
@jwt_required()
def get_learning_agreement(username, ida):
    auth = require_role("docente")
    if auth:
        return auth

    docente_id = get_jwt_identity()

    learningA = select(applicazione).where(
        applicazione.ida == ida, applicazione.username_docente == docente_id
    )
    learning_A = db.session.execute(learningA).scalars().first()
    if not learning_A:
        return jsonify({"msg": "applicazione non trovata"}), 404

    la = select(learningagreement).where(learningagreement.idla == learning_A.idla)
    la_ex = db.session.execute(la).scalars().first()
    if not la_ex:
        return jsonify({"msg": "learning agreement non presente"}), 404

    try:
        return send_from_directory(
            directory=CARTELLA_UPLOADS, path=la_ex.percorso_file, as_attachment=True
        )
    except FileNotFoundError:
        return jsonify({"msg": "file non trovato"}), 404


@bp_docente.route("/pratiche/<ida>", methods=["GET"])
@jwt_required()
def get_dettaglio_app(ida):
    auth = require_role("docente")
    if auth:
        return auth

    docente_id = get_jwt_identity()
    query = (
        select(applicazione, institution, pianoesami, learningagreement, utenti)
        .outerjoin(institution, applicazione.idin == institution.idin)
        .outerjoin(pianoesami, applicazione.ida == pianoesami.ida)
        .outerjoin(utenti, applicazione.username_studente == utenti.username)
        .outerjoin(learningagreement, applicazione.idla == learningagreement.idla)
        .where(applicazione.ida == ida, applicazione.username_docente == docente_id)
    )
    risultati = db.session.execute(query).all()

    if not risultati:
        return jsonify({"error": "Pratica non trovata"}), 404

    app = risultati[0][0]
    ist = risultati[0][1]
    learn = risultati[0][3]
    stud = risultati[0][4]

    # 3. Estrai l'elenco di TUTTI gli esami da TUTTE le righe
    # riga[2] corrisponde a 'pianoesami' nel tuo select(...) originale
    tutti_gli_esami = [row[2] for row in risultati]

    dettaglio = {
        "ida": app.ida,
        "stato": app.stato,
        "periodo": app.periodo_previsto,
        "transcriptofrecords": app.transcriptofrecords,
        "istituto": {
            "nome": ist.nome if ist else "Nessun istituto",
            "paese": ist.paese if ist else "-",
        },
        "studente": {
            "nome": stud.nome if stud else "Sconosciuto",
            "cognome": stud.cognome if stud else "",
            "username": stud.username if stud else "",
        },
        "learning_agreements": (
            [
                {
                    "id": learn.idla,
                    # Angular si aspetta 'filename', ma nel DB lo chiami 'percorso_file'
                    "filename": learn.percorso_file,
                    # Angular si aspetta 'stato' (es. per il badge), nel DB è 'accettato'
                    # Angular usa 'data_caricamento' (col pipe date:'dd/MM/yyyy'), nel DB è 'data'
                    "data_caricamento": learn.data,
                    # Questo ti tornerà utile se il docente rifiuta e deve mostrare il perché
                }
            ]
            if learn
            else []
        ),
        "pianoesami": [
            {
                # Cambia le chiavi (a sinistra) per farle combaciare ESATTAMENTE con l'HTML
                "id": e.idpe,  # Risolve il crash del "track esame.id"
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
            for e in tutti_gli_esami
            if e is not None
        ],
    }
    return jsonify(dettaglio), 200


@bp_docente.route("/learning-agreement/<string:idla>/valuta", methods=["PUT"])
@jwt_required()
def valuta_learning_agreement(idla):
    auth = require_role("docente")
    if auth:
        return auth

    dati = request.json
    decisione = dati.get("decisione")  # Riceverà 'Si' o 'No'
    motivazione = dati.get("motivazione", "")
    try:
        la = (
            db.session.execute(
                select(learningagreement).where(learningagreement.idla == idla)
            )
            .scalars()
            .first()
        )

        if not la:
            return jsonify({"msg": "Learning Agreement non trovato"}), 404

        la.stato = decisione
        la.motivazione = motivazione

        # 3. Aggiorna automaticamente lo stato della pratica (applicazione) collegata
        query = select(applicazione).where(applicazione.idla == idla)
        app = db.session.execute(query).scalars().first()
        query = select(learningagreement).where(learningagreement.idla == idla)
        learn = db.session.execute(query).scalars().first()
        if app:
            if decisione == "approvato":
                app.stato = "pre-partenza"
                learn.accettato = "Si"
            elif decisione == "rifiutato":
                app.stato = "creato"
                learn.accettato = "No"
            db.session.commit()
            print(decisione)
            return (
                jsonify({"msg": f"Learning Agreement valutato come: {decisione}"}),
                200,
            )
        else:
            return (
                jsonify({"error": "Pratica non trovata per questo Learning Agreement"}),
                404,
            )
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante l'aggiornamento dello stato: {e}")
        return jsonify({"error": "Errore interno del server"}), 500


@bp_docente.route("/esami/<string:idpe>/riconosci", methods=["PUT"])
@jwt_required()
def riconosci_esame(idpe):
    auth = require_role("docente")
    if auth:
        return auth

    dati = request.json
    decisione = dati.get("decisione")  # Riceverà 'approvato' o 'rifiutato'

    esame = (
        db.session.execute(select(pianoesami).where(pianoesami.idpe == idpe))
        .scalars()
        .first()
    )

    if not esame:
        return jsonify({"msg": "Esame non trovato"}), 404

    esame.stato = decisione

    app = (
        db.session.execute(select(applicazione).where(applicazione.ida == esame.ida))
        .scalars()
        .first()
    )

    if app and decisione == "approvato":

        esami_rimasti = (
            db.session.execute(
                select(pianoesami).where(
                    pianoesami.ida == app.ida, pianoesami.stato != "approvato"
                )
            )
            .scalars()
            .all()
        )

        if not esami_rimasti:
            app.stato = "completato"

    db.session.commit()
    return jsonify({"msg": f"Esame aggiornato con successo: {decisione}"}), 200
