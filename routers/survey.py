from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/survey/survey_begin.html")
async def get_survey_begin(request: Request):
    return templates.TemplateResponse("survey/survey_begin.html", {"request": request})

@router.get("/survey/survey_consent.html")
async def get_survey_consent(request: Request):
    return templates.TemplateResponse("survey/survey_consent.html", {"request": request})

@router.get("/survey/survey_end.html")
async def get_survey_end(request: Request):
    return templates.TemplateResponse("survey/survey_end.html", {"request": request})

@router.get("/survey/survey_PilarAmbiental.html")
async def get_survey_PilarAmbiental(request: Request):
    return templates.TemplateResponse("survey/survey_PilarAmbiental.html", {"request": request})

@router.get("/survey/survey_PilarGovernanca.html")
async def get_survey_PilarGovernanca(request: Request):
    return templates.TemplateResponse("survey/survey_PilarGovernanca.html", {"request": request})

@router.get("/survey/survey_PilarSocial.html")
async def get_survey_PilarSocial(request: Request):
    return templates.TemplateResponse("survey/survey_PilarSocial.html", {"request": request})

@router.get("/survey/survey_registration.html")
async def get_survey_registration(request: Request):
    return templates.TemplateResponse("survey/survey_registration.html", {"request": request})