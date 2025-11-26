"""
Configuración de conexión a base de datos
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# Crear engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log de queries en modo debug
    pool_pre_ping=True,   # Verificar conexión antes de usar
)

# Crear session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency para obtener sesión de base de datos.
    Usar con FastAPI Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa las tablas en la base de datos"""
    from models.database import Base
    Base.metadata.create_all(bind=engine)
