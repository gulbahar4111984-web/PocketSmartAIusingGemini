from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    tags=["Pages"]
)


templates = Jinja2Templates(
    directory="app/templates"
)


@router.get(
    "/",
    response_class=HTMLResponse,
)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        },
    )


@router.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request
        },
    )


@router.get(
    "/register",
    response_class=HTMLResponse,
)
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request
        },
    )


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request
        },
    )