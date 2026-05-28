from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    func,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# -----------------------------------
# Database Base
# -----------------------------------
Base = declarative_base()


# -----------------------------------
# Document Metadata Table
# -----------------------------------
class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)

    file_path = Column(Text, nullable=False)

    chunk_count = Column(Integer, nullable=False)

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


# -----------------------------------
# Upload Session Table
# -----------------------------------
class UploadSession(Base):
    __tablename__ = "upload_sessions"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        String(100),
        nullable=False,
        unique=True,
    )

    filename = Column(String(255), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


# -----------------------------------
# Retrieval Logs Table
# -----------------------------------
class RetrievalLog(Base):
    __tablename__ = "retrieval_logs"

    id = Column(Integer, primary_key=True, index=True)

    query = Column(Text, nullable=False)

    agent = Column(String(50), nullable=False)

    response_preview = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


# -----------------------------------
# Database Engine
# -----------------------------------
engine = create_engine(
    settings.POSTGRES_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# -----------------------------------
# Initialize Database
# -----------------------------------
def init_db() -> None:
    Base.metadata.create_all(bind=engine)


# -----------------------------------
# Store Document Metadata
# -----------------------------------
def store_document_metadata(
    filename: str,
    file_path: str,
    chunk_count: int,
) -> None:
    session = SessionLocal()

    try:
        document = DocumentMetadata(
            filename=filename,
            file_path=file_path,
            chunk_count=chunk_count,
        )

        session.add(document)
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


# -----------------------------------
# Create Upload Session
# -----------------------------------
def create_upload_session(
    session_id: str,
    filename: str,
) -> None:
    session = SessionLocal()

    try:
        upload_session = UploadSession(
            session_id=session_id,
            filename=filename,
        )

        session.add(upload_session)
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


# -----------------------------------
# Log Query
# -----------------------------------
def log_query(
    query: str,
    agent: str,
    response_preview: str,
) -> None:
    session = SessionLocal()

    try:
        log = RetrievalLog(
            query=query,
            agent=agent,
            response_preview=response_preview,
        )

        session.add(log)
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


# -----------------------------------
# Get Total Document Count
# -----------------------------------
def get_document_count() -> int:
    session = SessionLocal()

    try:
        return session.query(
            DocumentMetadata
        ).count()

    finally:
        session.close()


# -----------------------------------
# Get Total Indexed Chunks
# -----------------------------------
def get_total_chunks() -> int:
    session = SessionLocal()

    try:
        total = session.query(
            func.sum(DocumentMetadata.chunk_count)
        ).scalar()

        return total or 0

    finally:
        session.close()


# -----------------------------------
# Get Uploaded Documents
# -----------------------------------
def get_documents(limit: int = 10):
    session = SessionLocal()

    try:
        return (
            session.query(DocumentMetadata)
            .order_by(
                DocumentMetadata.uploaded_at.desc()
            )
            .limit(limit)
            .all()
        )

    finally:
        session.close()


# -----------------------------------
# Get Recent Retrieval Logs
# -----------------------------------
def get_recent_logs(limit: int = 10):
    session = SessionLocal()

    try:
        return (
            session.query(RetrievalLog)
            .order_by(
                RetrievalLog.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    finally:
        session.close()