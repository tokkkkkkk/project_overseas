import uuid
import random
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from datetime import date
from sqlalchemy import Date, Text, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from sqlalchemy import Table, Column, ForeignKey


def create_id(session, modello_applicazione):
    query = select(modello_applicazione.ida).order_by(modello_applicazione.ida.desc())
    ultimo_id = session.execute(query).scalars().first()

    if ultimo_id:
        # ultimo_id è una stringa tipo "APP015"
        # Prendiamo tutto dal 3° carattere in poi (cioè "015") e lo facciamo diventare numero intero (15)
        numero_attuale = int(ultimo_id[3:])
        nuovo_numero = numero_attuale + 1
    else:
        # Se il database è completamente vuoto, partiamo da 1
        nuovo_numero = 1

    # La vera magia di Python: formatta il numero con esattamente 3 cifre riempiendo di zeri!
    # Se nuovo_numero è 7 -> APP007. Se è 42 -> APP042.
    return f"APP{nuovo_numero:03d}"


def create_idLa(session, modello_applicazione):
    query = select(modello_applicazione.idla).order_by(modello_applicazione.idla.desc())
    ultimo_id = session.execute(query).scalars().first()

    if ultimo_id:
        # ultimo_id è una stringa tipo "APP015"
        # Prendiamo tutto dal 3° carattere in poi (cioè "015") e lo facciamo diventare numero intero (15)
        numero_attuale = int(ultimo_id[3:])
        nuovo_numero = numero_attuale + 1
    else:
        # Se il database è completamente vuoto, partiamo da 1
        nuovo_numero = 1

    # La vera magia di Python: formatta il numero con esattamente 3 cifre riempiendo di zeri!
    # Se nuovo_numero è 7 -> APP007. Se è 42 -> APP042.
    return f"LA{nuovo_numero:03d}"


def create_inst_id(session, modello_istituto):
    # ATTENZIONE: Assumo che la colonna chiave primaria si chiami 'idin' come nei codici precedenti.
    # Se nel tuo models.py si chiama diversamente (es. 'id'), cambialo in entrambe le occorrenze qui sotto!
    query = select(modello_istituto.idin).order_by(modello_istituto.idin.desc())
    ultimo_id = session.execute(query).scalars().first()

    if ultimo_id:
        # ultimo_id è una stringa tipo "INST01"
        # Prendiamo tutto dal 4° carattere in poi (cioè "01") e lo facciamo diventare numero intero (1)
        numero_attuale = int(ultimo_id[4:])
        nuovo_numero = numero_attuale + 1
    else:
        # Se il database è completamente vuoto, partiamo da 1
        nuovo_numero = 1

    # Formatta il numero con esattamente 2 cifre riempiendo di zeri!
    # Se nuovo_numero è 7 -> INST07. Se è 15 -> INST15.
    return f"INST{nuovo_numero:02d}"


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

vede_applicazione = Table(
    "vede_applicazione",
    Base.metadata,
    db.Column("ida", ForeignKey("applicazione.ida"), primary_key=True),
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

    app: Mapped[List["applicazione"]] = relationship(
        "applicazione", back_populates="docente_rel"
    )
    utente: Mapped["utenti"] = relationship(back_populates="fk_doc")

    # metodo to_dict
    def to_dict(self):
        return {
            "username": self.username,
            "nome": self.utente.nome,
            "cognome": self.utente.cognome,
        }


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

    app: Mapped["applicazione"] = relationship(back_populates="studente_rel")
    utente: Mapped["utenti"] = relationship(back_populates="fk_st")

    istituti: Mapped[list["institution"]] = relationship(
        "institution", secondary=vede_institution, back_populates="studente_view"
    )


class learningagreement(db.Model):
    __tablename__ = "learningagreement"
    idla: Mapped[str] = mapped_column(
        primary_key=True,
        unique=True,
        nullable=False,
    )
    accettato: Mapped[str] = mapped_column(
        db.Enum(
            "Si",
            "No",
            name="esito_accettazione",
            nullable=True,
        ),nullable=True
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)
    motivazione: Mapped[str] = mapped_column(nullable=True)
    username_docente: Mapped[str] = mapped_column(
        String, ForeignKey("docentireferenti.username")
    )
    percorso_file: Mapped[str]

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
            "username_docente": self.username_docente,
            "filename": getattr(self, "percorso_file", None),
        }


class pianoesami(db.Model):
    __tablename__ = "pianoesami"

    idpe: Mapped[int] = mapped_column(primary_key=True)
    codiceinsegnamentoestero: Mapped[str] = mapped_column(nullable=False)
    titoloinsegnamentoestero: Mapped[str] = mapped_column(nullable=False)
    creditiinsegnamentoestero: Mapped[int] = mapped_column(nullable=False)
    codiceinsegnamentocafoscari: Mapped[str] = mapped_column(nullable=False)
    titoloinsegnamentocafoscari: Mapped[str] = mapped_column(nullable=False)
    creditiinsegnamentocafoscari: Mapped[int] = mapped_column(nullable=False)
    stato: Mapped[str] = mapped_column(String(50), default='in attesa')
    ida: Mapped[int] = mapped_column(ForeignKey("applicazione.ida"))

    idapp: Mapped["applicazione"] = relationship("applicazione", back_populates="idpe")

    def to_dict(self):
        return {
            "idpe": self.idpe,
            "codice_estero": getattr(self, "codiceinsegnamentoestero", None),
            "titolo_estero": getattr(self, "titoloinsegnamentoestero", None),
            "crediti_estero": getattr(self, "creditiinsegnamentoestero", None),
            "codice_cafoscari": getattr(self, "codiceinsegnamentocafoscari", None),
            "titolo_cafoscari": getattr(self, "titoloinsegnamentocafoscari", None),
            "crediti_cafoscari": getattr(self, "creditiinsegnamentocafoscari", None),
            "stato": getattr(
                self, "stato", "in attesa"
            ),  # Se hai una colonna stato per l'esame
        }


class applicazione(db.Model):
    __tablename__ = "applicazione"

    ida: Mapped[str] = mapped_column(primary_key=True)
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
    esami: Mapped[bool] = mapped_column(nullable=True)
    transcriptofrecords: Mapped[str] = mapped_column(db.Enum("caricato", "null"))
    percorso_transcript: Mapped[str] = mapped_column(nullable=True)
    anno_accademico: Mapped[str] = mapped_column(nullable=True)
    periodo_previsto: Mapped[str]
    idin: Mapped[str] = mapped_column(ForeignKey("institution.idin"))
    username_studente: Mapped[str] = mapped_column(ForeignKey("studente.username"))
    username_docente: Mapped[str] = mapped_column(
        ForeignKey("docentireferenti.username")
    )
    idla: Mapped[str] = mapped_column(ForeignKey("learningagreement.idla"))

    # relationships
    # institution
    institution_rel: Mapped["institution"] = relationship(back_populates="app")
    # piano esami
    idpe: Mapped[List["pianoesami"]] = relationship(
        "pianoesami", back_populates="idapp"
    )
    # studente
    studente_rel: Mapped["studente"] = relationship(back_populates="app")
    # docente
    docente_rel: Mapped["docentireferenti"] = relationship(
        "docentireferenti", back_populates="app"
    )
    # learning agreement
    learning_agreement: Mapped["learningagreement"] = relationship(back_populates="ida")
    # ufficio overseas
    uffici: Mapped[list["ufficiooverseas"]] = relationship(
        "ufficiooverseas", secondary=vede_applicazione, back_populates="applicazioni"
    )

    # metodo to_dict
    def to_dict(self):
        return {
            "ida": self.ida,
            "stato": self.stato,
            "esami": self.esami,
            "username_studente": self.username_studente,
            "username_docente": self.username_docente,
            "idla": self.idla,
            "dataarrivo": self.dataarrivo.isoformat() if self.dataarrivo else None,
            "datapartenza": (
                self.datapartenza.isoformat() if self.datapartenza else None
            ),
            "periodo": self.periodo_previsto,
            "studente": {
                "nome": (
                    self.studente_rel.utente.nome
                    if self.studente_rel
                    else self.username_studente
                ),
                "cognome": (
                    self.studente_rel.utente.cognome if self.studente_rel else ""
                ),
            },
            "istituto": {
                "nome": (
                    self.institution_rel.nome
                    if self.institution_rel
                    else "Istituto sconosciuto"
                )
            },
            # CORRETTO: È un oggetto singolo, quindi lo mettiamo direttamente dentro una lista [ ]
            "learning_agreements": (
                [self.learning_agreement.to_dict()] if self.learning_agreement else []
            ),
            # CORRETTO: 'idpe' è già una lista (Mapped[List["pianoesami"]]), quindi il ciclo va benissimo
            "mapping_esami": [e.to_dict() for e in self.idpe] if self.idpe else [],
            "percorso_transcript": self.percorso_transcript,
        }


class institution(db.Model):
    __tablename__ = "institution"

    idin: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(unique=False, nullable=False)
    paese: Mapped[str] = mapped_column(nullable=False)
    citta: Mapped[str] = mapped_column("città", nullable=False)
    username_ufficio: Mapped[str] = mapped_column(
        ForeignKey("ufficiooverseas.username"), nullable=False
    )

    app: Mapped[List["applicazione"]] = relationship(back_populates="institution_rel")
    # Relazione molti-a-molti — lato opposto
    ufficio: Mapped[str] = relationship("ufficiooverseas", back_populates="istituto")
    studente_view: Mapped[list["studente"]] = relationship(
        "studente", secondary=vede_institution, back_populates="istituti"
    )

    # metodo to_dict
    def to_dict(self):
        return {
            "idin": self.idin,
            "nome": self.nome,
            "paese": self.paese,
            "città": self.citta,
            "citta": self.citta,
        }
        
class pianoesami_backup(db.Model):
    __tablename__ = "pianoesami_backup"
    
    idpe_backup: Mapped[int] = mapped_column(primary_key=True)
    ida: Mapped[str] = mapped_column(ForeignKey("applicazione.ida"))
    idpe_originale: Mapped[Optional[int]] = mapped_column(nullable=True)
    codiceinsegnamentoestero: Mapped[str] = mapped_column(nullable=False)
    titoloinsegnamentoestero: Mapped[str] = mapped_column(nullable=False)
    creditiinsegnamentoestero: Mapped[int] = mapped_column(nullable=False)
    codiceinsegnamentocafoscari: Mapped[str] = mapped_column(nullable=False)
    titoloinsegnamentocafoscari: Mapped[str] = mapped_column(nullable=False)
    creditiinsegnamentocafoscari: Mapped[int] = mapped_column(nullable=False)