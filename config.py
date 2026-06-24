import os


class Config:

    # Stringa di connessione a PostgreSQL
    # Formato: postgresql://utente:password@host:porta/nome_database
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:NduP5Mj9nCVxJyCK@db.nhdjencfjpmydjkzgzcd.supabase.co:5432/postgres"

    # Disabilita il tracciamento modifiche (non serve e rallenta)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cartella dove salvare i file caricati
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "app", "static", "uploads")

    # Dimensione massima file: 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    JWT_SECRET_KEY = "super-secret"
