from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.dbconfig.schemas import settings


# ==========================================
# DATABASE SERVER CONNECTION
# ==========================================

SERVER_URL = (
    f"mysql+pymysql://"
    f"{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:"
    f"{settings.DB_PORT}"
)


server_engine = create_engine(
    SERVER_URL,
    pool_pre_ping=True
)


# ==========================================
# CREATE DATABASE IF IT DOES NOT EXIST
# ==========================================

with server_engine.connect() as connection:

    connection.execute(
        text(
            f"CREATE DATABASE IF NOT EXISTS "
            f"`{settings.DB_NAME}`"
        )
    )

    connection.commit()


# ==========================================
# DATABASE CONNECTION
# ==========================================

DATABASE_URL = (
    f"mysql+pymysql://"
    f"{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:"
    f"{settings.DB_PORT}/"
    f"{settings.DB_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)


# ==========================================
# SESSION
# ==========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================
# BASE
# ==========================================

Base = declarative_base()


# ==========================================
# DATABASE DEPENDENCY
# ==========================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
