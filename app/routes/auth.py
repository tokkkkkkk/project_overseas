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
from app.models import (
    utenti,
)

bp_auth = Blueprint("auth", __name__)


@bp_auth.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@bp_auth.route("/login", methods=["POST"])
def login():
    utenti_table = utenti.__table__
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = utenti.query.filter_by(username=username).first()
        
    if not user or user.password != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)
