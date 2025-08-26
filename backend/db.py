
import os
from datetime import datetime
from sqlalchemy import create_engine, Integer, String, Text, TIMESTAMP, BigInteger, ForeignKey
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, sessionmaker
from sqlalchemy.sql import func

DB_URL = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER','cicd_user')}:{os.getenv('POSTGRES_PASSWORD','supersecret')}@{os.getenv('POSTGRES_HOST','postgres')}:{os.getenv('POSTGRES_PORT','5432')}/{os.getenv('POSTGRES_DB','cicd_health')}"

engine = create_engine(DB_URL, echo=False, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class Pipeline(Base):
    __tablename__ = "pipelines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(16), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    external_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)

class Build(Base):
    __tablename__ = "builds"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    pipeline_id: Mapped[int] = mapped_column(Integer, ForeignKey("pipelines.id", ondelete="CASCADE"))
    external_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    web_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_source: Mapped[str | None] = mapped_column(String(32), nullable=True)  # webhook | poll
    logs: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

def init_db():
    Base.metadata.create_all(engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
