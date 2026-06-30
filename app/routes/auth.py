from flask import Flask, request, jsonify, Blueprint
from app.models import utenti, studente, docentireferenti, ufficiooverseas, db
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

bp_auth = Blueprint("auth", __name__)


def get_ruolo(username):
    """Controlla in quale tabella si trova lo username per determinare il ruolo."""
    if studente.query.filter_by(username=username).one_or_none():
        return "studente"
    if docentireferenti.query.filter_by(username=username).one_or_none():
        return "docente"
    if ufficiooverseas.query.filter_by(username=username).one_or_none():
        return "ufficio"
    return None


@bp_auth.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@bp_auth.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = utenti.query.filter_by(username=username).one_or_none()

    # Fix: confronto con hash, non in chiaro
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Bad username or password"}), 401

    ruolo = get_ruolo(username)
    if not ruolo:
        return jsonify({"msg": "Utente senza ruolo assegnato"}), 403

    access_token = create_access_token(identity=username)

    # Risposta compatibile con il frontend Angular
    return jsonify({
        "token": access_token,
        "ruolo": ruolo,
        "utente": {
            "username": user.username,
            "nome": user.nome,
            "cognome": user.cognome,
            "ruolo": ruolo
        }
    }), 200


@bp_auth.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({"msg": "Preflight OK"}), 200

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    nome = request.json.get("nome", None)
    cognome = request.json.get("cognome", None)
    # 1. Recupera il ruolo richiesto da Angular
    ruolo = request.json.get("ruolo", None) 

    if not username or not password or not nome or not cognome or not ruolo:
        return jsonify({"msg": "Dati mancanti"}), 400

    hashed_password = generate_password_hash(password)
    user = utenti(username=username, password=hashed_password, nome=nome, cognome=cognome)

    try:
        db.session.add(user)
        db.session.flush() # Salva temporaneamente per avere l'utente disponibile
        
        # 2. Inserisci l'utente nella tabella corretta in base al ruolo
        if ruolo == "studente":
            # 1. Cerchiamo l'ultimo studente ordinando le matricole in ordine decrescente
            ultimo_studente = studente.query.order_by(studente.matricola.desc()).first()
            
            # 2. Generiamo la nuova matricola
            if ultimo_studente and ultimo_studente.matricola:
                # Se esiste già uno studente, prendiamo la sua matricola, la trasformiamo in numero, sommiamo 1 e la facciamo tornare stringa
                nuova_matricola = str(int(ultimo_studente.matricola) + 1)
            else:
                # Se il database è vuoto e questo è il primissimo studente, partiamo da una base
                nuova_matricola = "90001"
                
            # 3. Salviamo il nuovo studente con la matricola sequenziale
            nuovo_studente = studente(username=username, matricola=nuova_matricola) 
            db.session.add(nuovo_studente)
        elif ruolo == "docente":
            nuovo_docente = docentireferenti(username=username)
            db.session.add(nuovo_docente)
        elif ruolo == "ufficio":
            nuovo_ufficio = ufficiooverseas(username=username)
            db.session.add(nuovo_ufficio)
        else:
            return jsonify({"msg": "Ruolo non valido"}), 400

        db.session.commit()
        return jsonify({"msg": "Utente registrato con successo!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Registration failed", "error": str(e)}), 400