import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, aliased
from sqlalchemy import Integer, String, select, delete
from app.models import (
    applicazione,
    institution,
    studente,
    learningagreement,
    docentireferenti,
    utenti,
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
    query = (
        select(applicazione, institution, utenti)
        .where(applicazione.username_studente == studente_id)
        .join(institution, applicazione.idin == institution.idin)
        .join(utenti, applicazione.username_docente == utenti.username)
    )
    app = db.session.execute(query).all()
    # messo all al posto di first, dato che angular si aspetta una lista

    if not app:
        return jsonify([]), 200

    lista_pratiche = []
    for app, ist, doc in app:
        lista_pratiche.append(
            {
                "ida": app.ida,
                # strutture di invio dati per restituirli uguali a come sono richiesti nel file del frontend
                "anno_accademico": app.anno_accademico,
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


# per la query doppia su utenti
studente = aliased(utenti)
docente = aliased(utenti)


@bp_studente.route("/pratiche/<ida>", methods=["GET"])
@jwt_required()
def dettaglio_applicazione_studente(ida):
    studente_id = get_jwt_identity()
    query = (
        select(applicazione, institution, pianoesami, studente, docente)
        .outerjoin(institution, applicazione.idin == institution.idin)
        .outerjoin(pianoesami, applicazione.ida == pianoesami.ida)
        .outerjoin(studente, applicazione.username_studente == studente.username)
        .outerjoin(docente, applicazione.username_docente == docente.username)
        .where(applicazione.ida == ida, applicazione.username_studente == studente_id)
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

    print("ssss", dati)

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
            codiceinsegnamentoestero=e["codice_estero"],
            titoloinsegnamentoestero=e["titolo_estero"],
            creditiinsegnamentoestero=e["crediti_estero"],
            codiceinsegnamentocafoscari=e["codice_cafoscari"],
            titoloinsegnamentocafoscari=e["titolo_cafoscari"],
            creditiinsegnamentocafoscari=e["crediti_cafoscari"],
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


@bp_studente.route("/elimina/<ida>", methods=["DELETE"])
def delete_pratica(ida):
    try:
        # 1. Trova la pratica
        app_to_delete = db.session.get(applicazione, ida)

        if not app_to_delete:
            return jsonify({"error": "Pratica non trovata"}), 404

        idla_da_cancellare = app_to_delete.idla

        db.session.execute(delete(pianoesami).where(pianoesami.ida == ida))

        db.session.delete(app_to_delete)
        db.session.flush()  # forza aggiornamento per liberare  LA

        if idla_da_cancellare:
            db.session.execute(
                delete(learningagreement).where(
                    learningagreement.idla == idla_da_cancellare
                )
            )

        db.session.commit()

        return (
            jsonify({"message": "Pratica e dati collegati eliminati con successo!"}),
            200,
        )

    except Exception as e:
        db.session.rollback()
        print(
            f"\n--- ERRORE ELIMINAZIONE A CASCATA ---\n{str(e)}\n-------------------------------------\n"
        )
        return jsonify({"error": "Errore interno durante l'eliminazione"}), 500
