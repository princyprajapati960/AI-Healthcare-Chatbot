from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend.app.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from backend.app.models import schemas_db  # noqa: F401
    
    # Import enhanced schemas for medical knowledge base and audit logging
    try:
        from backend.app.models import enhanced_schemas  # noqa: F401
    except ImportError:
        pass  # Enhanced schemas only available with PostgreSQL

    Base.metadata.create_all(bind=engine)
