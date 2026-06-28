from flask import Flask, flash, redirect, render_template, request, url_for, Blueprint
from flask import jsonify

# 2. Database & ORM
from app.models import utenti
import sqlalchemy as sq

# 3. Security & Hashing (Flask-Bcrypt replaces passlib)


from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from app.models import utenti, db
from werkzeug.security import check_password_hash, generate_password_hash

bp_auth = Blueprint("auth", __name__)


@bp_auth.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@bp_auth.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = utenti.query.filter_by(username=username).one_or_none()

    # check_password_hash(user.password, password)
    if not user or not user.password == password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


@bp_auth.route("/register", methods=["POST"])
def register():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    nome = request.json.get("nome", None)
    cognome = request.json.get("cognome", None)

    hashed_password = generate_password_hash(password)
    user = utenti(
        username=username, password=hashed_password, nome=nome, cognome=cognome
    )

    # check_password_hash(user.password, password)
    if not username or not password or not nome or not cognome:
        return jsonify({"msg": "Missing Data"}), 401

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"msg": "User successfully registered!"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Database error during commit: {e}")  # 2. Print database errors if any
        return jsonify({"msg": "Registration failed", "error": str(e)}), 400
