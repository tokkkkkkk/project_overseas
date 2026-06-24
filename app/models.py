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
from sqlalchemy import Table, Column, ForeignKey


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

vede_applicazione = Table(
    "vede_applicazione",
    Base.metadata,
    db.Column("idin", ForeignKey("applicazione.ida"), primary_key=True),
    db.Column(
        "username_ufficio", ForeignKey("ufficiooverseas.username"), primary_key=True
    ),
)

vede_institution = Table(
    "vede_institution",
    Base.metadata,
    db.Column("idin", ForeignKey("institution.idin"), primary_key=True),
    db.Column(
        "username_ufficio", ForeignKey("ufficiooverseas.username"), primary_key=True
    ),
)


class utenti(UserMixin, db.Model):
    __tablename__ = "utenti"

    username: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    cognome: Mapped[str] = mapped_column(unique=False, nullable=False)
    nome: Mapped[str] = mapped_column(nullable=False)
    fk_st: Mapped[List["studente"]] = relationship()
    fk_uf: Mapped[List["ufficiooverseas"]] = relationship()
    fk_doc: Mapped[List["docentireferenti"]] = relationship()

    def get_id(self):
        return str(self.username)


class docentireferenti(db.Model):
    __tablename__ = "docentireferenti"

    learningagreement: Mapped[List["learningagreement"]] = relationship(
        "learningagreement", back_populates="docentireferenti"
    )
    username: Mapped[int] = mapped_column(
        ForeignKey("utenti.username"), primary_key=True, unique=True, nullable=False
    )


class ufficiooverseas(db.Model):
    __tablename__ = "ufficiooverseas"
    username: Mapped[int] = mapped_column(
        ForeignKey("utenti.username"), primary_key=True, unique=True, nullable=False
    )

    # Relazione molti-a-molti tramite la tabella ponte
    istituti: Mapped[list["institution"]] = relationship(
        "Institution", secondary=vede_institution, back_populates="uffici"
    )
    applicazioni: Mapped[list["ufficiooverseas"]] = relationship(
        "UfficioOverseas", secondary=vede_applicazione, back_populates="uffici"
    )


class studente(db.Model):
    __tablename__ = "studente"

    username: Mapped[int] = mapped_column(
        ForeignKey("utenti.username"), primary_key=True, unique=True, nullable=False
    )
    matricola: Mapped[str] = mapped_column(unique=True, nullable=False)


class learningagreement(db.Model):
    __tablename__ = "learningagreement"
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
    username_docente: Mapped[str] = mapped_column(
        String, ForeignKey("docentireferenti.username")
    )
    ida: Mapped[List["applicazione"]] = relationship()


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
    idpa: Mapped[List["pianoesami"]] = relationship()
    idla: Mapped[int] = mapped_column(ForeignKey("learningagreement.idla"))
    # Relazione molti-a-molti — lato opposto
    uffici: Mapped[list["ufficiooverseas"]] = relationship(
        "ufficioOverseas", secondary=vede_applicazione, back_populates="applicazioni"
    )


class institution(db.Model):
    __tablename__ = "institution" 
    
    idin: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(unique=False, nullable=False)
    paese: Mapped[str] = mapped_column(nullable=False)
    citta: Mapped[str] = mapped_column(nullable=False)
    username_ufficio: Mapped[str] = mapped_column(
        ForeignKey("ufficiooverseas.username"), nullable=False
    )
    # Relazione molti-a-molti — lato opposto
    uffici: Mapped[list["ufficiooverseas"]] = relationship(
        "ufficioOverseas", secondary=vede_institution, back_populates="istituti"
    )