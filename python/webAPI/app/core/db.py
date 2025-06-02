from sqlmodel import Session, create_engine, select

from app.config import settings

if settings.USE_DB:
    engine = create_engine(str(settings.DATABASE_URL), echo=True)
else:
    engine = None