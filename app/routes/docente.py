import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, delete, select, update
from datetime import date

from app.models import (
    applicazione,
    pianoesami,
    pianoesami_backup,
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
    
    # 2. Carica la pratica (verificando che appartenga al docente)
    app = db.session.execute(
        select(applicazione).where(
            applicazione.ida == ida, 
            applicazione.username_docente == docente_id
        )
    ).scalars().first()

    if not app:
        return jsonify({"error": "Pratica non trovata o non autorizzata"}), 404

    # 3. Carica i dati correlati in modo esplicito
    db.session.expire_all()
    esami = db.session.execute(
        select(pianoesami).where(pianoesami.ida == ida)
    ).scalars().all()
    
    ist = db.session.get(institution, app.idin)
    stud = db.session.get(utenti, app.username_studente)
    learn = db.session.get(learningagreement, app.idla)

    # 4. Costruisci il dizionario di risposta
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
        "learning_agreements": [
            {
                "id": learn.idla,
                "filename": learn.percorso_file,
                "data_caricamento": learn.data,
            }
        ] if learn else [],
        "pianoesami": [
            {
                "id": e.idpe,
                "codice_estero": e.codiceinsegnamentoestero,
                "titolo_estero": e.titoloinsegnamentoestero,
                "crediti_estero": e.creditiinsegnamentoestero,
                "codice_cafoscari": e.codiceinsegnamentocafoscari,
                "titolo_cafoscari": e.titoloinsegnamentocafoscari,
                "crediti_cafoscari": e.creditiinsegnamentocafoscari,
                "stato": e.stato,
                "voto_ottenuto": e.voto_ottenuto, 
                "data_superamento": e.data_superamento.isoformat() if e.data_superamento else None
            }
            for e in esami
        ]
        
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
                db.session.execute(
                    update(pianoesami)
                        .where(pianoesami.ida == app.ida)
                        .values(stato="approvato")
                )
            elif decisione == "rifiutato":
                learn.accettato = "No"
                
                # Distingui tra rifiuto iniziale e rifiuto di modifica
                if app.dataarrivo and app.datapartenza:
                    # È una modifica durante la mobilità — non annullare
                    # lo stato rimane invariato
                    app.stato="in corso"
                else:
                    # È il primo LA — annulla la pratica
                    app.stato = "annullato"
                
                # Ripristina esami dal backup (in entrambi i casi)
                backup_esami = db.session.execute(
                    select(pianoesami_backup).where(pianoesami_backup.ida == app.ida)
                ).scalars().all()
                
                if backup_esami:
                    # Elimina esami attuali
                    db.session.execute(
                        delete(pianoesami).where(pianoesami.ida == app.ida)
                    )
                    db.session.flush()
                    
                    # Ripristina dal backup
                    for b in backup_esami:
                        ripristinato = pianoesami(
                            ida=b.ida,
                            codiceinsegnamentoestero=b.codiceinsegnamentoestero,
                            titoloinsegnamentoestero=b.titoloinsegnamentoestero,
                            creditiinsegnamentoestero=b.creditiinsegnamentoestero,
                            codiceinsegnamentocafoscari=b.codiceinsegnamentocafoscari,
                            titoloinsegnamentocafoscari=b.titoloinsegnamentocafoscari,
                            creditiinsegnamentocafoscari=b.creditiinsegnamentocafoscari,
                        )
                        db.session.add(ripristinato)
                    
                    # Elimina il backup dopo il ripristino
                    db.session.execute(
                        delete(pianoesami_backup).where(pianoesami_backup.ida == app.ida)
                    )
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
            app.stato = "viaggioCompletato"

    db.session.commit()
    return jsonify({"msg": f"Esame aggiornato con successo: {decisione}"}), 200
