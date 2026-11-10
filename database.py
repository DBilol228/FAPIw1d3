from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./medbook.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

def get_db():
    with SessionLocal() as db:
        yield db
