from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List, Optional
from functools import lru_cache
from loguru import logger

Base = declarative_base()


class PaperModel(Base):
    __tablename__ = "papers"
    
    paper_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    authors = Column(JSON)
    abstract = Column(Text)
    publication_date = Column(DateTime)
    source = Column(String)
    source_url = Column(String)
    pdf_url = Column(String)
    pdf_path = Column(String)
    doi = Column(String)
    full_text = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AnalysisModel(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(Text, nullable=False)
    papers_analyzed = Column(Integer)
    agents_used = Column(Integer)
    results = Column(JSON)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelVersionModel(Base):
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_type = Column(String, nullable=False)
    version = Column(String, nullable=False)
    provider = Column(String)
    capabilities = Column(JSON)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class Database:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info(f"Database initialized: {database_url}")
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def save_paper(self, paper_data: dict) -> None:
        session = self.get_session()
        try:
            paper = session.query(PaperModel).filter_by(paper_id=paper_data["paper_id"]).first()
            if paper:
                for key, value in paper_data.items():
                    setattr(paper, key, value)
            else:
                paper = PaperModel(**paper_data)
                session.add(paper)
            session.commit()
            logger.debug(f"Saved paper: {paper_data['paper_id']}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving paper: {e}")
            raise
        finally:
            session.close()
    
    def get_paper(self, paper_id: str) -> Optional[dict]:
        session = self.get_session()
        try:
            paper = session.query(PaperModel).filter_by(paper_id=paper_id).first()
            if paper:
                return {
                    "paper_id": paper.paper_id,
                    "title": paper.title,
                    "authors": paper.authors,
                    "abstract": paper.abstract,
                    "publication_date": paper.publication_date,
                    "source": paper.source,
                    "source_url": paper.source_url,
                    "pdf_url": paper.pdf_url,
                    "pdf_path": paper.pdf_path,
                    "doi": paper.doi,
                    "full_text": paper.full_text,
                    "metadata": paper.metadata,
                }
            return None
        finally:
            session.close()
    
    def save_analysis(self, analysis_data: dict) -> int:
        session = self.get_session()
        try:
            analysis = AnalysisModel(**analysis_data)
            session.add(analysis)
            session.commit()
            logger.debug(f"Saved analysis: {analysis.id}")
            return analysis.id
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving analysis: {e}")
            raise
        finally:
            session.close()
    
    def get_recent_analyses(self, limit: int = 10) -> List[dict]:
        session = self.get_session()
        try:
            analyses = session.query(AnalysisModel).order_by(
                AnalysisModel.created_at.desc()
            ).limit(limit).all()
            
            return [{
                "id": a.id,
                "query": a.query,
                "papers_analyzed": a.papers_analyzed,
                "agents_used": a.agents_used,
                "results": a.results,
                "confidence_score": a.confidence_score,
                "created_at": a.created_at
            } for a in analyses]
        finally:
            session.close()
    
    def save_model_version(self, model_data: dict) -> None:
        session = self.get_session()
        try:
            model = ModelVersionModel(**model_data)
            session.add(model)
            session.commit()
            logger.info(f"Registered model: {model_data['model_type']} v{model_data['version']}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving model version: {e}")
            raise
        finally:
            session.close()
    
    def get_active_models(self) -> List[dict]:
        session = self.get_session()
        try:
            models = session.query(ModelVersionModel).filter_by(is_active=1).all()
            return [{
                "id": m.id,
                "model_type": m.model_type,
                "version": m.version,
                "provider": m.provider,
                "capabilities": m.capabilities,
                "created_at": m.created_at
            } for m in models]
        finally:
            session.close()


@lru_cache()
def get_database(database_url: str = "sqlite:///./research_platform.db") -> Database:
    return Database(database_url)
