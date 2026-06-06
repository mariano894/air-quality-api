from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# URL de conexión: mysql+mysqlconnector://user:pass@host:port/db
DATABASE_URL = (
    f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # verifica conexión antes de usarla
    pool_recycle=3600,        # recicla conexiones cada hora
    pool_size=10,             # conexiones simultáneas en el pool
    max_overflow=20,          # conexiones extra permitidas sobre pool_size
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency para inyectar sesión de BD en cada request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
