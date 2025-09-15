# <<< COLLE ICI LE CODE PYTHON CI-DESSUS, sans rien ajouter >>>
import os
import sys
from pathlib import Path

# Ajoute la racine du projet au PYTHONPATH (…/freshkeeper-backend-phase3)
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

# Récupère l'URL DB depuis l'environnement (ou alembic.ini si absent)
from alembic import context

db_url = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URL")
if db_url:
    context.config.set_main_option("sqlalchemy.url", db_url)

# >>> adapte ICI l'import du Base selon ton projet
# Essaye d'abord freshkeeper.database, sinon app.database
try:
    from freshkeeper.database import Base  # si ton paquet s'appelle freshkeeper
except ModuleNotFoundError:
    from app.database import Base  # fallback si ton paquet s'appelle app


# Essaie plusieurs emplacements possibles pour Base
try:
    from app.database import Base  # si ton paquet s’appelle "app"
except ModuleNotFoundError:
    try:
        from freshkeeper.database import Base  # si finalement "freshkeeper" existe
    except ModuleNotFoundError:
        # Dernier recours : adapte ici le bon chemin vers Base
        from database import Base  # ex: si database.py est à la racine

# ou selon ton arborescence :
# from freshkeeper.models import Base

import os
import sys

# --- ensure project root on sys.path ---
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # dossier racine du projet
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
# ---------------------------------------


target_metadata = Base.metadata

from alembic import context

config = context.config

# Si l’URL n’est pas définie dans alembic.ini, prendre DATABASE_URL
if not config.get_main_option("sqlalchemy.url"):
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        config.set_main_option("sqlalchemy.url", db_url)

# puis, plus bas, après fileConfig(...), importe la metadata du projet
from freshkeeper.database import Base

target_metadata = Base.metadata
