from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/")
async def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/home.html")
async def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
