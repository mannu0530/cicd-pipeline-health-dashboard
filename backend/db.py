
import os
from datetime import datetime
from sqlalchemy import create_engine, Integer, String, Text, TIMESTAMP, BigInteger, ForeignKey, Boolean, inspect
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
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

def run_migrations():
    """Run database migrations to handle schema updates"""
    inspector = inspect(engine)
    
    # Check if pipelines table exists
    if not inspector.has_table("pipelines"):
        return
    
    # Check if is_active column exists in pipelines table
    columns = [col['name'] for col in inspector.get_columns("pipelines")]
    
    if "is_active" not in columns:
        print("Adding is_active column to pipelines table...")
        with engine.connect() as conn:
            conn.execute("ALTER TABLE pipelines ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL")
            conn.commit()
        print("✅ Added is_active column successfully")

def init_db():
    """Initialize database with tables and run migrations"""
    # Create tables
    Base.metadata.create_all(engine)
    
    # Run migrations
    run_migrations()

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
