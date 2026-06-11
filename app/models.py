from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from datetime import date
from sqlalchemy import Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class utenti(UserMixin, db.Model):
    __tablename__ = "utenti"

    username: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    cognome: Mapped[str] = mapped_column(unique=False, nullable=False)
    nome: Mapped[str] = mapped_column(nullable=False)

    def get_id(self):
        return str(self.username)


class pianoesami(db.Model):
    __tablename__ = "pianoesami"

    idpa: Mapped[int] = mapped_column(primary_key=True)
    codiceinsegnamentoestero: Mapped[str] = mapped_column(nullable=False)
    titoloinsegnamentoestero: Mapped[str] = mapped_column(nullable=False)
    creditiinsegnamentoestero: Mapped[int] = mapped_column(nullable=False)
    codiceinsegnamentocafoscari: Mapped[str] = mapped_column(nullable=False)
    titoloinsegnamentocafoscari: Mapped[str] = mapped_column(nullable=False)
    creditiinsegnamentocafoscari: Mapped[int] = mapped_column(nullable=False)
    ida: Mapped[int] = mapped_column(ForeignKey("applicazione.ida"))


class applicazione(db.Model):
    __tablename__ = "applicazione"

    ida: Mapped[int] = mapped_column(primary_key=True)
    stato: Mapped[str] = mapped_column(
        db.Enum(
            "creato",
            "in attesa",
            "pre-partenza",
            "in corso",
            "completato",
            "annullato",
            name="stato_applicazione",
            nullable=False,
        )
    )
    dataarrivo: Mapped[date] = mapped_column(nullable=True)
    datapartenza: Mapped[date] = mapped_column(nullable=True)
    


class studente(db.model):
    username: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
    matricola: Mapped[str] = mapped_column(unique=True, nullable=False)


vede_institution = Table(
    "vede_institution",
    Base.metadata,
    db.Column("idin", ForeignKey("institution.idin"), primary_key=True),
    db.Column("username_ufficio", ForeignKey("ufficiooverseas.username"), primary_key=True),
)


class istitution(db.model):
    idin: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(unique=False, nullable=False)
    paese: Mapped[str] = mapped_column(nullable=False)
    citta: Mapped[str] = mapped_column(nullable=False)
    username_ufficio: Mapped[str] = mapped_column(ForeignKey("ufficiooverseas.username"), nullable=False)
    # Relazione molti-a-molti — lato opposto
    uffici: Mapped[list["ufficioOverseas"]] = relationship(
        "ufficioOverseas",
        secondary=vede_institution,
        back_populates="istituti"
    )


class ufficiooverseas(db.Model):
    username: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
     # Relazione molti-a-molti tramite la tabella ponte
    istituti: Mapped[list["Institution"]] = relationship(
        "Institution",
        secondary=vede_institution,
        back_populates="uffici"
    )
    


class docentireferenti(db.Model):

    __tablename__ = "docentireferenti"
    username: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)

    learningagreement: Mapped[List["learningagreement"]] = relationship(
        "learningagreement", back_populates="docentireferenti"
    )


class learningagreement(db.Model):
    __tablename__ = "learningagreemen"
    idla: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
    accettato: Mapped[str] = mapped_column(
        db.Enum(
            "approvato",
            "rifiutato",
            "in attesa",
            name="esito_accettazione",
            nullable=False,
        )
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)
    motivazione: Mapped[str] = mapped_column(nullable=False)
