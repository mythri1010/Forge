import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()

# Import Flask app and models
from app import create_app
from app.extensions import db
import app.models  # noqa: F401

# Create Flask app
flask_app = create_app()

# Alembic Config object
alembic_config = context.config

# Fix postgres:// to postgresql:// for SQLAlchemy 2.x
db_url = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://", 1)
if db_url:
    alembic_config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging if present
if alembic_config.config_file_name is not None:
    if os.path.exists(alembic_config.config_file_name):
        fileConfig(alembic_config.config_file_name)

# Target metadata for autogenerate
target_metadata = db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = alembic_config.get_main_option("sqlalchemy.url")
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
    
    def process_revision_directives(context, revision, directives):
        if getattr(alembic_config.cmd_opts, 'autogenerate', False):
            if directives[0].upgrade_ops.is_empty():
                directives[:] = []

    # Use Flask app's engine
    with flask_app.app_context():
        connectable = db.engine

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                process_revision_directives=process_revision_directives,
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
