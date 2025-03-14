from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db:5432/survey_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    eixo_pergunta = Column(String, nullable=False)  # Axis the question belongs to
    pergunta = Column(Text, nullable=False)         # Question text
    tema = Column(Text, nullable=False)
    criterio = Column(Text, nullable=False)
    tipo = Column(Text, nullable=False)
    nivel = Column(Integer, nullable=False)

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    empresa = Column(String, nullable=False)
    atividade = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    cidade = Column(String, nullable=False)

class SurveyInfo(Base):
    __tablename__ = "surveys"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    producaomes = Column(Float, nullable=False)
    unidproducao = Column(String, nullable=False)
    
    company = relationship("Company")
    
class SurveyAnswers(Base):
    __tablename__ = "survey_answers"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    eixo = Column(String, nullable=False)  # Axis the answers belong to
    answer = Column(Text, nullable=False)

    company = relationship("Company")
    question = relationship("Question")
    surveyinfo = relationship("SurveyInfo")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
