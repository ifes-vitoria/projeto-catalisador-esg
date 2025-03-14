from typing import List, Tuple, cast
import copy
import pandas as pd
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import pdfkit
from contextlib import asynccontextmanager

from database import get_db, Base, engine
from models import Survey, SurveyMeta, SurveyAmbiental, SurveyGovernanca, SurveySocial, SurveyClass
from db_manager import insert_survey_data
from report_main import report_generation
from report.models import Data, Empresa, Pergunta, Indicador
from database import Company, Question, SurveyInfo, SurveyAnswers
from routers import home, survey

import sys
sys.path.append('/app')

# Create tables on app startup using lifespan
@asynccontextmanager
async def lifespan_context(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    # Add any cleanup code here if needed

app = FastAPI(lifespan=lifespan_context)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Template directory
templates = Jinja2Templates(directory="templates")

# Include Routers
app.include_router(home.router)
app.include_router(survey.router)

def get_all_surveys(metadata: SurveyMeta, db: Session) -> Tuple[List[Survey], pd.DataFrame]:
    existing_company = db.query(Company).filter_by(
        empresa=metadata.empresa,
        atividade=metadata.atividade,
        estado=metadata.estado,
        cidade=metadata.cidade,
    ).first()

    if existing_company is None:
        return [], pd.DataFrame()

    questions = db.query(Question).all()
    questions_df = pd.DataFrame([s.__dict__ for s in questions])
    questions_df = questions_df.drop(columns=['_sa_instance_state'])

    survey_data = db.query(SurveyInfo).filter_by(company_id=existing_company.id).all()
    survey_df = pd.DataFrame([s.__dict__ for s in survey_data])
    survey_df = survey_df.drop(columns=['_sa_instance_state'])

    survey_answer_data = db.query(SurveyAnswers).filter_by(company_id=int(existing_company.id)).all()
    survey_answer_df = pd.DataFrame([s.__dict__ for s in survey_answer_data])
    survey_answer_df = survey_answer_df.drop(columns=['_sa_instance_state'])

    df_amb_names = pd.DataFrame({k:[v] for k,v in SurveyAmbiental._name_mapping.default.items()}).T.reset_index()
    df_amb_names.columns = ['varname', 'question_id']

    df_soc_names = pd.DataFrame({k:[v] for k,v in SurveySocial._name_mapping.default.items()}).T.reset_index()
    df_soc_names.columns = ['varname', 'question_id']

    df_gov_names = pd.DataFrame({k:[v] for k,v in SurveyGovernanca._name_mapping.default.items()}).T.reset_index()
    df_gov_names.columns = ['varname', 'question_id']

    survey_list = []
    for survey_uni_id in  survey_answer_df.survey_id.unique():
        survey_df_date = survey_df[survey_df.id == survey_uni_id]
        survey_answer_df_date = survey_answer_df[survey_answer_df.survey_id == survey_uni_id]
        survey_answer_governanca_df = survey_answer_df_date[survey_answer_df_date.eixo=='governanca'][['question_id', 'answer']]
        survey_answer_governanca_df = survey_answer_governanca_df.merge(df_gov_names, on='question_id', how='left')[['varname', 'answer']]
        survey_answer_ambiental_df = survey_answer_df_date[survey_answer_df_date.eixo=='ambiental'][['question_id', 'answer']]
        survey_answer_ambiental_df = survey_answer_ambiental_df.merge(df_amb_names, on='question_id', how='left')[['varname', 'answer']]
        survey_answer_social_df = survey_answer_df_date[survey_answer_df_date.eixo=='social'][['question_id', 'answer']]
        survey_answer_social_df = survey_answer_social_df.merge(df_soc_names, on='question_id', how='left')[['varname', 'answer']]
        
        social_dict = {}
        for x in survey_answer_social_df.to_dict('records'):
            social_dict[x['varname']] = x['answer']
            
        governance_dict = {}
        for x in survey_answer_governanca_df.to_dict('records'):
            governance_dict[x['varname']] = x['answer']
            
        ambiental_dict = {}
        for x in survey_answer_ambiental_df.to_dict('records'):
            ambiental_dict[x['varname']] = x['answer']
            
        survey_dict = {
            'meta': {
                'empresa': existing_company.empresa,
                'atividade': existing_company.atividade,
                'estado': existing_company.estado,
                'cidade': existing_company.cidade,
                'producaomes': str(survey_df_date.producaomes.iloc[0]),
                'unidproducao': survey_df_date.unidproducao.iloc[0],
                'data': survey_df_date.date.iloc[0].strftime('%d/%m/%Y')
            },
            'social': social_dict,
            'governanca': governance_dict,
            'ambiental': ambiental_dict
        }
        survey_list.append(Survey(**survey_dict))
    return survey_list, questions_df

def build_single_data_from_survey(survey: Survey, questio_df: pd.DataFrame) -> Data:
    perguntas = []
    indicadores = []
    pergunta_df = questio_df[questio_df.tipo == 'Pergunta']
    indicador_df = questio_df[questio_df.tipo == 'Indicador']
    for eixo, survey_eixo_now in [
            ('social', survey.social),
            ('governanca', survey.governanca),
            ('ambiental', survey.ambiental)
        ]:
        survey_eixo_now = cast(SurveyClass, survey_eixo_now)
        pergunta_df_eixo = pergunta_df[pergunta_df.eixo_pergunta == eixo]
        indicador_df_eixo = indicador_df[indicador_df.eixo_pergunta == eixo]
        for _, pergunta_now in pergunta_df_eixo.iterrows():
            perguntas.append(Pergunta(
                nivel=int(pergunta_now.nivel),
                name=str(pergunta_now.pergunta),
                resposta=str(survey_eixo_now.get_by_id(pergunta_now.id)),
                eixo=str(eixo.capitalize()),
                tema=str(pergunta_now.tema),
                criterio=str(pergunta_now.criterio)
            ))
        for _, indicador_now in indicador_df_eixo.iterrows():
            valor = survey_eixo_now.get_by_id(indicador_now.id)
            indicadores.append(Indicador(
                eixo=str(eixo.capitalize()),
                item=str(indicador_now.pergunta),
                valor=float(valor) if valor is not None else 0.0  # Tratando o caso de valor None
            ))
    data = Data(
        empresa=Empresa(
            nome_empresa=survey.meta.empresa,
            producaomes=survey.meta.producaomes,
            unidproducao=survey.meta.unidproducao,
            data=survey.meta.data.strftime('%d/%m/%Y'),
            localizacao=f'{survey.meta.cidade} - {survey.meta.estado}'
        ),
        perguntas=perguntas,
        indicadores=indicadores
    )
    return data

def report_generation_wrapper(list_of_survey: List[Survey], questio_df: pd.DataFrame) -> str:
    list_of_data = []
    for survey in list_of_survey:
        data = build_single_data_from_survey(survey, questio_df)
        list_of_data.append(data)
    report_html = report_generation(list_of_data)

    pdf_path = "report.pdf"
    pdfkit.from_string(report_html, pdf_path)
    
    return pdf_path  # Retornando o caminho do arquivo PDF gerado  

@app.get("/report-generation")
async def generate_report(metadata: SurveyMeta, db: Session = Depends(get_db)):
    list_of_survey_data, questio_df = get_all_surveys(metadata, db)
    if len(list_of_survey_data) == 0:
        return {"message": "No survey data found"}
    pdf_path = report_generation_wrapper(list_of_survey_data, questio_df)
    return FileResponse(path=pdf_path, filename="report.pdf", media_type="application/pdf")

@app.post("/submit-survey")
async def submit_survey(survey_data: Survey, db: Session = Depends(get_db)):
    try:
        insert_survey_data(survey_data, db)
        list_of_survey_data, question_df = get_all_surveys(survey_data.meta, db)
        if len(list_of_survey_data) == 0:
            return {"message": "No survey data found"}
        pdf_path = report_generation_wrapper(list_of_survey_data, question_df)
        return FileResponse(path=pdf_path, filename="report.pdf", media_type="application/pdf")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
