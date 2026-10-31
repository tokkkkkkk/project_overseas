# Overseas mobility portal

Showcase project for a university mobility application, with a Flask API and
an Angular frontend. It is not a production-ready service and contains no
real user data or demo credentials.

## Repository hygiene

- Secrets and database connection strings are loaded from environment
  variables.
- Uploaded documents, local databases, caches, and dependency folders are
  excluded from version control.
- The upload directory is intentionally empty in the public repository.

If a credential was ever committed before publishing this repository, revoke
or rotate it even if the file is later deleted from the working tree or Git
history.

## Backend

Create a virtual environment and install the dependencies:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

The API starts at `http://localhost:5000`. Export `DATABASE_URL`,
`SECRET_KEY`, and `JWT_SECRET_KEY` in your shell or hosting environment when
using a non-local database. The `.env.example` file documents the required
variables; the application does not load `.env` files automatically.

## Frontend

```powershell
cd app\overseas-frontend
npm ci
npm start
```

The Angular development server starts at `http://localhost:4200`.
