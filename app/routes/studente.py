import flask, os
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, aliased
from sqlalchemy import Integer, String, select, delete
from app.models import (
    applicazione,
    institution,
    pianoesami_backup,
    studente,
    learningagreement,
    docentireferenti,
    utenti,
    db,
)
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import jsonify, request, Blueprint, redirect
from app.models import pianoesami, applicazione, create_id, create_idLa
from datetime import date, datetime
from werkzeug.utils import secure_filename
import traceback

bp_studente = Blueprint(
    "studente",
    __name__,
)
CARTELLA_UPLOADS = os.path.join(os.getcwd(), "app", "static", "uploads")
ALLOWED_EXTENSIONS = {"pdf"}


def require_role(expected_role):
    """Controlla che il token dello studente abbia il ruolo richiesto."""
    claims = get_jwt()
    allowed_roles = (
        {expected_role} if isinstance(expected_role, str) else set(expected_role)
    )
    if claims.get("ruolo") not in allowed_roles:
        return jsonify({"msg": "Accesso non autorizzato"}), 403


# Restituisce tutte le pratiche associate allo studente autenticato.
@bp_studente.route("/pratiche", methods=["GET"])
@jwt_required()
def get_my_app():
    auth = require_role("studente")
    if auth:
        return auth

    studente_id = get_jwt_identity()
    query = (
        select(applicazione, institution, utenti)
        .where(applicazione.username_studente == studente_id)
        .join(institution, applicazione.idin == institution.idin)
        .join(utenti, applicazione.username_docente == utenti.username)
    )
    app = db.session.execute(query).all()
    # La frontend si aspetta una lista di pratiche, quindi restituiamo sempre un elenco.

    if not app:
        return jsonify([]), 200

    lista_pratiche = []
    # Costruisce il formato dei dati che il frontend usa per mostrare le pratiche.
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


# Aggiorna i dati di viaggio di una pratica, come data di partenza e data di arrivo.
@bp_studente.route("/pratiche/<ida>", methods=["PUT"])
@jwt_required()
def update_applicazione_studente(ida):
    try:
        auth = require_role("studente")
        if auth:
            return auth
        dati = request.json
        studente_id = get_jwt_identity()
        query = select(applicazione).where(
            applicazione.ida == ida, applicazione.username_studente == studente_id
        )
        risultati = db.session.execute(query).scalars().first()

        if not risultati:
            return jsonify({"error": "Pratica non trovata"}), 404

        # Se il frontend invia una nuova data di partenza, la salva nel record.
        if "data_partenza" in dati:
            val_p = dati["data_partenza"]
            risultati.datapartenza = val_p if val_p else None

        # Se il frontend invia una nuova data di arrivo, la salva nello stesso modo.
        if "data_arrivo" in dati:
            val_a = dati["data_arrivo"]
            risultati.dataarrivo = val_a if val_a else None

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("====== ERROR DETAILS ======")
        traceback.print_exc()
        print("===========================")

        # And this sends the error directly to your Angular console
        return (
            jsonify({"error": f"Crash Type: {type(e).__name__} | Message: {str(e)}"}),
            500,
        )

    return jsonify({"msg": "suiccess"}), 200


# Mostra il dettaglio completo di una pratica, inclusi istituto, docente, studente ed esami.
@bp_studente.route("/pratiche/<ida>", methods=["GET"])
@jwt_required()
def dettaglio_applicazione_studente(ida):
    auth = require_role("studente")
    if auth:
        return auth

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

    # Unisce i dati della pratica con tutti gli esami restituiti dalla query.
    tutti_gli_esami = [row[2] for row in risultati]

    dettaglio = {
        "ida": app.ida,
        "stato": app.stato,
        "periodo": app.periodo_previsto,
        "data_arrivo": app.dataarrivo,
        "data_partenza": app.datapartenza,
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


# Crea una nuova pratica e prepara il relativo piano di esami.
@bp_studente.route("/pratiche", methods=["POST"])
@jwt_required()
def create_myapp():
    auth = require_role("studente")
    if auth:
        return auth

    studente_id = get_jwt_identity()
    dati = request.json
    nuovo_ida = create_id(db.session, applicazione)
    anno_acc = dati["anno_accademico"]
    istituto_id = dati["istituto_id"]
    periodo = dati["periodo"]
    docente = dati["docente_id"]

    # Crea la pratica iniziale con lo stato di attesa.
    app = applicazione(
        ida=nuovo_ida,
        stato="in attesa",
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

    # Aggiunge gli esami ricevuti dal frontend al nuovo record della pratica.
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
    try:
        db.session.commit()
        return jsonify({"ida": app.ida, "id": app.ida}), 201
    except Exception as e:
        db.session.rollback()
        print({e})
        return jsonify({"error": "Errore interno durante l'eliminazione"}), 500


# Carica un learning agreement per una pratica e lo salva nella cartella dedicata.
@bp_studente.route("/pratiche/<ida>/learning-agreement", methods=["POST"])
@jwt_required()
def get_my_la(ida):
    auth = require_role("studente")
    if auth:
        return auth

    docente = db.session.execute(
        select(applicazione.username_docente).where(applicazione.ida == ida)
    ).scalar()
    nuovo_idla = create_idLa(db.session, learningagreement)
    file = request.files["fileselezionato"]

    if file.filename == "":
        return jsonify({"msg": "Nessun file selezionato"}), 400

    # Salva il file caricato in modo sicuro nella cartella delle uploads.
    filename = secure_filename(f"{nuovo_idla}_{file.filename}")
    full_path = os.path.join(CARTELLA_UPLOADS, filename)
    file.save(full_path)

    # Crea il record del learning agreement e lo collega alla pratica.
    la = learningagreement(
        idla=nuovo_idla,
        accettato=None,
        data=date.today(),
        username_docente=docente,
        percorso_file=filename,
    )
    query = select(applicazione).where(applicazione.ida == ida)
    get = db.session.execute(query).scalars().first()

    get.idla = nuovo_idla
    get.stato = "in attesa"
    db.session.add(la)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")  # <--- THIS IS THE KEY!
        return jsonify({"msg": "Errore interno del server durante il salvataggio"}), 500
    return jsonify({"msg": "Learning Agreement caricato con successo"}), 200


# Restituisce l'elenco degli istituti disponibili per lo studente o l'ufficio.
@bp_studente.route("/istituti", methods=["GET"])
@jwt_required()
def get_my_institution():
    auth = require_role(("studente", "ufficio"))
    if auth:
        return auth

    query = select(institution)
    institution_db = db.session.execute(query).scalars().all()
    return jsonify([istituti.to_dict() for istituti in institution_db]), 200


# Restituisce i docenti referenti disponibili nel sistema.
@bp_studente.route("/docente", methods=["GET"])
@jwt_required()
def get_my_docente():
    auth = require_role("studente")
    if auth:
        return auth

    query = select(docentireferenti)
    docentireferenti_db = db.session.execute(query).scalars().all()
    return jsonify([docenti.to_dict() for docenti in docentireferenti_db]), 200


# Elimina una pratica e i dati collegati, compreso il learning agreement eventuale.
@bp_studente.route("/elimina/<ida>", methods=["DELETE"])
@jwt_required()
def delete_pratica(ida):
    auth = require_role("studente")
    if auth:
        return auth

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
        return jsonify({"error": "Errore interno durante l'eliminazione"}), 500


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Carica il transcript di una pratica, se la pratica è in uno stato valido.
@bp_studente.route("/pratiche/<string:ida>/transcript", methods=["POST"])
@jwt_required()
def carica_transcript(ida):
    auth = require_role("studente")
    if auth:
        return auth

    studente_id = get_jwt_identity()

    # Verifica che la pratica appartenga davvero allo studente autenticato.
    pratica = (
        db.session.execute(
            select(applicazione).where(
                applicazione.ida == ida, applicazione.username_studente == studente_id
            )
        )
        .scalars()
        .first()
    )

    if not pratica:
        return jsonify({"msg": "Pratica non trovata"}), 404

    if pratica.stato not in ["in corso", "pre-partenza"]:
        return jsonify({"msg": "Non puoi caricare il transcript in questo stato"}), 400

    if "file" not in request.files:
        return jsonify({"msg": "Nessun file caricato"}), 400

    file = request.files["file"]

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"msg": "File non valido, deve essere PDF"}), 400

    # Salva il file nel percorso dedicato alle uploads.
    filename = secure_filename(f"transcript_{ida}_{file.filename}")
    filepath = os.path.join(CARTELLA_UPLOADS, filename)
    os.makedirs(CARTELLA_UPLOADS, exist_ok=True)
    file.save(filepath)

    # Aggiorna la pratica
    pratica.transcriptofrecords = "caricato"
    pratica.percorso_transcript = filename
    db.session.commit()

    return (
        jsonify({"msg": "Transcript caricato con successo", "filename": filename}),
        200,
    )


# Aggiorna il piano degli esami di una pratica, creando un backup prima delle modifiche.
@bp_studente.route("/applicazione/<string:ida>/esami", methods=["PUT"])
@jwt_required()
def aggiorna_piano_esami(ida):
    try:
        auth = require_role("studente")
        if auth:
            return auth
        app = (
            db.session.execute(select(applicazione).where(applicazione.ida == ida))
            .scalars()
            .first()
        )
        if not app or app.stato not in ["pre-partenza", "in attesa", "rifiutato","in corso"]:
            return jsonify({"msg": "Modifica non consentita in questo stato"}), 403

        esami_correnti = (
            db.session.execute(select(pianoesami).where(pianoesami.ida == ida))
            .scalars()
            .all()
        )

        # Elimina eventuali backup precedenti prima di crearne uno nuovo.
        db.session.execute(
            delete(pianoesami_backup).where(pianoesami_backup.ida == ida)
        )

        # Salva gli esami attuali nel backup come riferimento.
        for e in esami_correnti:
            backup = pianoesami_backup(
                ida=e.ida,
                idpe_originale=e.idpe,
                codiceinsegnamentoestero=e.codiceinsegnamentoestero,
                titoloinsegnamentoestero=e.titoloinsegnamentoestero,
                creditiinsegnamentoestero=e.creditiinsegnamentoestero,
                codiceinsegnamentocafoscari=e.codiceinsegnamentocafoscari,
                titoloinsegnamentocafoscari=e.titoloinsegnamentocafoscari,
                creditiinsegnamentocafoscari=e.creditiinsegnamentocafoscari,
            )
            db.session.add(backup)

        db.session.flush()

        esami_ricevuti = request.json
        print(f"DEBUG: Esami ricevuti: {esami_ricevuti}")

        ids_ricevuti = [
            e.get("idpe") or e.get("id")
            for e in esami_ricevuti
            if (e.get("idpe") or e.get("id"))
        ]

        # Elimina dal database gli esami che non compaiono più nella nuova lista.
        db.session.execute(
            delete(pianoesami).where(
                pianoesami.ida == ida, pianoesami.idpe.not_in(ids_ricevuti)
            )
        )

        # Aggiorna o crea gli esami in base ai dati ricevuti dal frontend.
        for item in esami_ricevuti:
            idpe = item.get("idpe") or item.get("id")
            print(f"DEBUG item: {item}")
            print(f"DEBUG idpe: {idpe}")

            if idpe == 0 or idpe is None:
                nuovo = pianoesami(
                    ida=ida,
                    codiceinsegnamentoestero=item.get("codice_estero"),
                    titoloinsegnamentoestero=item.get("titolo_estero"),
                    creditiinsegnamentoestero=item.get("crediti_estero"),
                    codiceinsegnamentocafoscari=item.get("codice_cafoscari"),
                    titoloinsegnamentocafoscari=item.get("titolo_cafoscari"),
                    creditiinsegnamentocafoscari=item.get("crediti_cafoscari"),
                )
                db.session.add(nuovo)
                print(f"DEBUG: aggiunto nuovo esame {nuovo}")
                db.session.flush()
                print(f"DEBUG: flush completato, idpe assegnato: {nuovo.idpe}")

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("====== ERROR DETAILS ======")
        traceback.print_exc()
        print("===========================")

        # And this sends the error directly to your Angular console
        return (
            jsonify({"error": f"Crash Type: {type(e).__name__} | Message: {str(e)}"}),
            500,
        )
    print("DEBUG: commit completato")
    return jsonify({"msg": "Piano esami aggiornato!"}), 200


# Registra i voti inseriti dallo studente per gli esami della pratica.
@bp_studente.route("/applicazione/<string:ida>/registra-voti", methods=["PUT"])
@jwt_required()
def registra_voti(ida):
    auth = require_role("studente")
    if auth: return auth
    
    # Recupera la lista di voti inviata dal frontend per gli esami della pratica.
    voti_ricevuti = request.json  # es: [{"idpe": 1, "voto": "30", "data": "2026-07-01"}, ...]
    
    for item in voti_ricevuti:
        idpe = item.get("idpe")
        esame = db.session.get(pianoesami, idpe)
        
        # Verifica che l'esame appartenga davvero a questa pratica prima di salvarne il voto.
        if esame and esame.ida == ida:
            esame.voto_ottenuto = item.get("voto")
            # Converti la stringa data in oggetto date se necessario
            esame.data_superamento = item.get("data") 
            
    db.session.commit()
    return jsonify({"msg": "Voti aggiornati con successo"}), 200