from sqlalchemy.orm import Session
from models import Survey, SurveyAmbiental, SurveyGovernanca, SurveySocial
from database import engine, SessionLocal, Base, Question, Company, SurveyInfo, SurveyAnswers
import pandas as pd

def load_questions_from_csv(csv_path: str, db: Session):
    df = pd.read_csv(csv_path)
    query = db.query(Question.id, Question.eixo_pergunta, Question.pergunta)
    existing_questions = pd.read_sql(query.statement, db.bind)
    existing_questions_set = set(existing_questions[['id', 'eixo_pergunta']].apply(tuple, axis=1))
    df = df[~df[['id_pergunta', 'eixo_pergunta']].apply(tuple, axis=1).isin(existing_questions_set)]
    
    df['id_pergunta'] = df['id_pergunta'].astype(int)
    df['eixo_pergunta'] = df['eixo_pergunta'].astype(str)
    df['pergunta'] = df['pergunta'].astype(str)
    df['nivel'] = df['nivel'].astype(int)
    df['tema'] = df['tema'].astype(str)
    df['criterio'] = df['criterio'].astype(str)
    df['tipo'] = df['tipo'].astype(str)

    if df.shape[0]:
        for _, row in df.iterrows():
            question = Question(
                id=int(row.id_pergunta),
                eixo_pergunta=str(row.eixo_pergunta),
                pergunta=str(row.pergunta),
                tema=str(row.tema),
                criterio=str(row.criterio),
                tipo=str(row.tipo),
                nivel=int(row.nivel)
            )
            db.add(question)
            db.commit()

def insert_survey_data(survey_data: Survey, db: Session):
    
    existing_company = db.query(Company).filter_by(
        empresa=survey_data.meta.empresa,
        atividade=survey_data.meta.atividade,
        estado=survey_data.meta.estado,
        cidade=survey_data.meta.cidade
    ).first()

    if not existing_company:
        # Insert company data
        company = Company(
            empresa=survey_data.meta.empresa,
            atividade=survey_data.meta.atividade,
            estado=survey_data.meta.estado,
            cidade=survey_data.meta.cidade,
        )
        db.add(company)
        db.commit()
        db.refresh(company)
    else:
        company = existing_company
        
    survey_info = SurveyInfo(
        date=survey_data.meta.data,
        company_id=company.id,
        producaomes = float(survey_data.meta.producaomes),
        unidproducao = survey_data.meta.unidproducao
    )
    # Insert survey info
    db.add(survey_info)
    db.commit()
    db.refresh(survey_info)
    
    # Insert survey data
    for eixo_name, eixo_data in {
        "ambiental": (survey_data.ambiental, SurveyAmbiental._name_mapping.default),
        "governanca": (survey_data.governanca, SurveyGovernanca._name_mapping.default),
        "social": (survey_data.social, SurveySocial._name_mapping.default)
    }.items():
        current_data, mapping_data = eixo_data
        for question, answer in current_data.dict(exclude_none=True).items():
            question_id = mapping_data[question]
            db.add(
                SurveyAnswers(
                    company_id=company.id,
                    survey_id=survey_info.id,
                    question_id=question_id,
                    eixo=eixo_name,
                    answer=answer
                )
            )
    db.commit()

# Usage
if __name__ == "__main__":
    db = SessionLocal()
    # Create tables
    Base.metadata.create_all(bind=engine)
    load_questions_from_csv("questions.csv", db)
    db.close()