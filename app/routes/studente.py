import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

from app.models import applicazione, studente, learningagreement, docentireferenti
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request, Blueprint

bp_studente = Blueprint(
    "studente",
    __name__,
)
