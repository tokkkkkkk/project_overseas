from flask import Flask, request, jsonify, Blueprint
from app.models import utenti, studente, docentireferenti, ufficiooverseas, db
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

bp_auth = Blueprint("auth", __name__)


def get_ruolo(username):
    """Determina il ruolo dell'utente cercando lo username nelle tabelle specifiche."""
    if studente.query.filter_by(username=username).one_or_none():
        return "studente"
    if docentireferenti.query.filter_by(username=username).one_or_none():
        return "docente"
    if ufficiooverseas.query.filter_by(username=username).one_or_none():
        return "ufficio"
    return None


# Endpoint di prova che restituisce l'utente attualmente autenticato tramite token JWT.
@bp_auth.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# Effettua il login verificando username, password e ruolo dell'utente.
@bp_auth.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    # Cerca l'utente nel database e verifica la password hashata.
    user = utenti.query.filter_by(username=username).one_or_none()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Recupera il ruolo dell'utente in base alla tabella in cui è registrato.
    ruolo = get_ruolo(username)
    if not ruolo:
        return jsonify({"msg": "Utente senza ruolo assegnato"}), 403

    # Genera il token JWT che verrà usato per le richieste successive.
    access_token = create_access_token(
        identity=username, additional_claims={"ruolo": ruolo}
    )

    # Restituisce il token e i dati essenziali dell'utente al frontend.
    return (
        jsonify(
            {
                "token": access_token,
                "ruolo": ruolo,
                "utente": {
                    "username": user.username,
                    "nome": user.nome,
                    "cognome": user.cognome,
                    "ruolo": ruolo,
                },
            }
        ),
        200,
    )


# Registra un nuovo utente e lo inserisce nella tabella corretta in base al ruolo.
@bp_auth.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({"msg": "Preflight OK"}), 200

    # Legge i dati inviati dal frontend per la creazione dell'account.
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    nome = request.json.get("nome", None)
    cognome = request.json.get("cognome", None)
    # Recupera il ruolo richiesto dal frontend.
    ruolo = request.json.get("ruolo", None)

    if not username or not password or not nome or not cognome or not ruolo:
        return jsonify({"msg": "Dati mancanti"}), 400

    # Cripta la password prima di salvarla nel database.
    hashed_password = generate_password_hash(password)
    user = utenti(
        username=username, password=hashed_password, nome=nome, cognome=cognome
    )

    try:
        db.session.add(user)
        db.session.flush()  # Salva temporaneamente per avere l'utente disponibile

        # Inserisce l'utente nella tabella corrispondente al ruolo scelto.
        if ruolo == "studente":
            ultimo_studente = studente.query.order_by(studente.matricola.desc()).first()

            # Se esiste già uno studente, incrementa la matricola precedente.
            if ultimo_studente and ultimo_studente.matricola:
                nuova_matricola = str(int(ultimo_studente.matricola) + 1)
            else:
                nuova_matricola = "90001"

            # Salva il nuovo studente con la matricola assegnata.
            nuovo_studente = studente(username=username, matricola=nuova_matricola)
            db.session.add(nuovo_studente)
        elif ruolo == "docente":
            # Crea il profilo docente collegato all'utente.
            nuovo_docente = docentireferenti(username=username)
            db.session.add(nuovo_docente)
        elif ruolo == "ufficio":
            # Crea il profilo ufficio collegato all'utente.
            nuovo_ufficio = ufficiooverseas(username=username)
            db.session.add(nuovo_ufficio)
        else:
            return jsonify({"msg": "Ruolo non valido"}), 400

        db.session.commit()
        return jsonify({"msg": "Utente registrato con successo!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Registration failed", "error": str(e)}), 400
