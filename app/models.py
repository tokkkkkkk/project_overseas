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
    db.Column("username_studente", ForeignKey("studente.username"), primary_key=True),
)


class utenti(UserMixin, db.Model):
    __tablename__ = "utenti"

    username: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    cognome: Mapped[str] = mapped_column(unique=False, nullable=False)
    nome: Mapped[str] = mapped_column(nullable=False)
    fk_st: Mapped[List["studente"]] = relationship(back_populates="utente")
    fk_uf: Mapped[List["ufficiooverseas"]] = relationship(back_populates="utente")
    fk_doc: Mapped[List["docentireferenti"]] = relationship(back_populates="utente")

    def get_id(self):
        return str(self.username)


class docentireferenti(db.Model):
    __tablename__ = "docentireferenti"

    learningagreement: Mapped[List["learningagreement"]] = relationship()
    username: Mapped[str] = mapped_column(
        ForeignKey("utenti.username"), primary_key=True, unique=True, nullable=False
    )

    app:Mapped[List["applicazione"]]=relationship("applicazione", back_populates="docente_rel")
    utente: Mapped["utenti"] = relationship(back_populates="fk_doc")



class ufficiooverseas(db.Model):
    __tablename__ = "ufficiooverseas"
    username: Mapped[str] = mapped_column(
        ForeignKey("utenti.username"), primary_key=True, unique=True, nullable=False
    )

    utente: Mapped["utenti"] = relationship(back_populates="fk_uf")
    # Relazione molti-a-molti tramite la tabella ponte

    applicazioni: Mapped[list["ufficiooverseas"]] = relationship(
        "applicazione", secondary=vede_applicazione, back_populates="uffici"
    )

    istituto: Mapped[list["ufficiooverseas"]] = relationship(
        "institution", back_populates="ufficio"
    )


class studente(db.Model):
    __tablename__ = "studente"

    username: Mapped[int] = mapped_column(
        ForeignKey("utenti.username"), primary_key=True, unique=True, nullable=False
    )
    matricola: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    app:Mapped["applicazione"]=relationship(back_populates="studente_rel")
    utente: Mapped["utenti"] = relationship(back_populates="fk_st")
    
    istituti: Mapped[list["institution"]] = relationship(
        "institution", secondary=vede_institution, back_populates="studente_view"
    )


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
    docente: Mapped["docentireferenti"] = relationship(
        back_populates="learningagreement"
    )
    ida: Mapped["applicazione"] = relationship(back_populates="learning_agreement")

    def to_dict(self):
        return {
            "idla": self.idla,
            "accettato": str(self.accettato) if self.accettato else None,
            "data": self.data.isoformat() if self.data else None,
            "motivazione": self.motivazione,
            "username_docente": self.username_docente
        }


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

    idapp:Mapped[str] = relationship("applicazione", back_populates="idpe")


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
            "viaggioCompletato",
            name="stato_applicazione",
            nullable=False,
        )
    )
    dataarrivo: Mapped[date] = mapped_column(nullable=True)
    datapartenza: Mapped[date] = mapped_column(nullable=True)
    esami:Mapped[bool]= mapped_column(nullable=True)
    transcriptofrecords: Mapped[str] = mapped_column(
        db.Enum(
            "caricato",
            "null"
        )
    )
    idin:Mapped[str]=mapped_column(ForeignKey("institution.idin"))
    username_studente: Mapped[str] = mapped_column(ForeignKey("studente.username"))
    username_docente:Mapped[str]=mapped_column(ForeignKey("docentireferenti.username"))
    idla: Mapped[str] = mapped_column(ForeignKey("learningagreement.idla"))
    
    
    #relationships
    #institution
    institution_rel:Mapped["institution"]=relationship(back_populates="app")
    #piano esami
    idpe: Mapped[List["pianoesami"]] = relationship("pianoesami", back_populates="idapp")
    #studente
    studente_rel: Mapped["studente"] = relationship(back_populates="app")
    #docente
    docente_rel: Mapped["docentireferenti"] = relationship("docentireferenti", back_populates="app")
    #learning agreement
    learning_agreement: Mapped["learningagreement"] = relationship(back_populates="ida")
    #ufficio overseas
    uffici: Mapped[list["ufficiooverseas"]] = relationship(
        "ufficiooverseas", secondary=vede_applicazione, back_populates="applicazioni"
    )

    #metodo to_dict
    def to_dict(self):
        return {
            "ida": self.ida,
            "stato": self.stato,
            "esami": self.esami,
            "username_studente": self.username_studente,
            "username_docente": self.username_docente,
            "idla": self.idla,
            "dataarrivo": self.dataarrivo.isoformat() if self.dataarrivo else None,
            "datapartenza": self.datapartenza.isoformat() if self.datapartenza else None
        }


class institution(db.Model):
    __tablename__ = "institution"

    idin: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(unique=False, nullable=False)
    paese: Mapped[str] = mapped_column(nullable=False)
    citta: Mapped[str] = mapped_column(nullable=False)
    username_ufficio: Mapped[str] = mapped_column(
        ForeignKey("ufficiooverseas.username"), nullable=False
    )

    app: Mapped[List["applicazione"]] = relationship(back_populates= "institution_rel")
    # Relazione molti-a-molti — lato opposto
    ufficio: Mapped[str] = relationship("ufficiooverseas", back_populates="istituto")
    studente_view: Mapped[list["studente"]] = relationship(
        "studente", secondary=vede_institution, back_populates="istituti"
    )
