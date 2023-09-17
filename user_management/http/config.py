"""Configuration of the app file."""
import os
from collections.abc import AsyncGenerator
from typing import Any

from myem_lib.db_settings_mixins import DbSettingsMixin
from myem_lib.fast_api_settings_mixins import FastApiSettingsMixin
from myem_lib.nameko_settings_mixins import NamekoSettingsMixin
from pydantic import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from user_management import private_key, rsa_key


class Settings(BaseSettings, NamekoSettingsMixin, FastApiSettingsMixin, DbSettingsMixin):
    """Settings for the application."""

    private_key: str = private_key
    public_key: str = rsa_key.export_to_pem()
    available_roles: list[str] = os.environ["USER_MANAGEMENT_AVAILABLE_ROLES"].split("|")
    registrable_roles: list[str] = os.environ["USER_MANAGEMENT_REGISTRABLE_ROLES"].split("|")
    token_expiration_in_seconds = int(os.environ["TOKEN_EXPIRATION_IN_SECONDS"])



settings = Settings()


async_engine = create_async_engine(
    f"postgresql+asyncpg://elfjaqaf:pldYeSi2O4Sbh8HlIpV7a6OtcYeSUSj1@mahmud.db.elephantsql.com/elfjaqaf?prepared_statement_cache_size=0",
    connect_args={"timeout": 31536000},
    pool_pre_ping=True,
)

async_session_maker = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Async session generator."""
    async with async_session_maker() as _session:
        yield _session


engine = create_engine(
    settings.db_uri,
    connect_args={
        "connect_timeout": 31536000,
        "keepalives": 1,
        "keepalives_idle": 60,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
    pool_pre_ping=True,
)
_conn = engine.connect()
session = sessionmaker(bind=engine)


def get_db() -> Any:
    """Get database instance."""
    db = session()
    try:
        yield db
    finally:
        db.close()