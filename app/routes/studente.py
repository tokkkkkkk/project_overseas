import flask
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, select

from app.models import applicazione, studente, learningagreement, docentireferenti, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request, Blueprint, redirect
from app.models import pianoesami, applicazione, create_id

bp_studente = Blueprint(
    "studente",
    __name__,
)


@bp_studente.route("/my_applicazione", methods=["GET"])
@jwt_required()
def get_my_app():
    studente_id = get_jwt_identity()

    query = select(applicazione).where(applicazione.username_studente == studente_id)

    app = db.session.execute(query).scalars().first()
    if not app:
        return (
            jsonify(
                {
                    "msg": "lo studente non possiede un'applicazione, crearne una",
                    "has_application": False,
                }
            ),
            200,
        )

    data = app.to_dict()
    if app.stato in ("in riconoscimento esami", "completato"):
        data["esami"] = [e.to_dict() for e in app.esami]

    return jsonify({"has_application": True, "applicazione": app.to_dict()}), 200


@bp_studente.route("/create_applicazione", methods=["PUT"])
@jwt_required()
def create_myapp():
    studente_id = get_jwt_identity()
    dati = request.json

    nuovi_esami = [
        pianoesami(
            applicazione_id=dati["applicazione_id"],
            codice_estero=e["codice_estero"],
            titolo_estero=e["titolo_estero"],
            crediti_estero=e["crediti_estero"],
            codice_cafoscari=e["codice_cafoscari"],
            titolo_cafoscari=e["titolo_cafoscari"],
            crediti_cafoscari=e["crediti_cafoscari"],
        )
        for e in dati["esami"]
    ]

    db.session.add_all(nuovi_esami)
    db.session.commit()

    nuovo_ida = create_id(sq.session, applicazione)
    anno_acc = dati["anno_accademico"]
    istituto = dati["istituto"]
    periodo = dati["periodo"]
    docente = dati["docente"]

    app = applicazione(
        ida=nuovo_ida,
        stato="creato",
        esami=False,
        transcriptofrecords=False,
        idin=istituto,
        username_studente=studente_id,
        username_docente=docente,
        anno_accademico=anno_acc,
        periodo_previsto=periodo,
    )

    db.session.add(app)
    db.session.commit()
