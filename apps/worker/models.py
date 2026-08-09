from datetime import datetime
from sqlalchemy import String, DateTime, Integer, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"
    id:           Mapped[str]      = mapped_column(String(36), primary_key=True)
    status:       Mapped[str]      = mapped_column(String(20), default="queued")  # queued|processing|done|failed
    original_key: Mapped[str]      = mapped_column(String(255)) # S3 key of the original image
    error:        Mapped[str]      = mapped_column(String(500), default="")
    created_at:   Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at:   Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    attempts: Mapped[int] = mapped_column(Integer, default=0)

def init_db():
    Base.metadata.create_all(engine)