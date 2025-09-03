import os
import sys
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# Ajouter la racine du projet au PYTHONPATH (?/migrations/.. -> racine)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Charger .env
load_dotenv()

config = context.config

# R?cup?rer l'URL de la base depuis l'env
db_url = os.environ.get("DATABASE_URL", "")

# Alembic travaille plus simplement en mode sync.
# On convertit l'URL async (postgresql+asyncpg://...) en URL sync (postgresql://...)
sync_url = db_url.replace("+asyncpg", "") if db_url else db_url
if sync_url:
    config.set_main_option("sqlalchemy.url", sync_url)

# Logging config (d?pend d'alembic.ini)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importer metadata de SQLAlchemy (vos mod?les)
from app.db.base import Base  # type: ignore
from app.models import user  # assure l'import des tables

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
