import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.database import Base, DATABASE_URL  # Use your actual Base and DB URL
from app.models import models  # This is necessary to make Alembic "see" your models

# Load config from alembic.ini
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load model metadata for 'autogenerate'
target_metadata = Base.metadata


# === OFFLINE MIGRATIONS (No DB connection) ===
def run_migrations_offline() -> None:
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# === ONLINE MIGRATIONS (With DB connection) ===
def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(DATABASE_URL, future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# Run the appropriate migration
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())