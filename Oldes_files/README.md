# FrigoApp Backend avec PostgreSQL

## Installation
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Base de données
Édite `.env` et configure ton mot de passe :
```
DATABASE_URL=postgresql+asyncpg://frigo_user:motdepasse@localhost:5432/frigoapp
```

## Migrations
```
alembic upgrade head
```

## Lancer le serveur
```
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Endpoints
- POST /auth/register
- POST /auth/login
