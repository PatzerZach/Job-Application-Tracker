from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="presentation/templates")

auth_controller = None

@router.get("/", response_class=HTMLResponse)
def show_landing_page(request: Request):
    return templates.TemplateResponse(
        "landing.html",
        {
            "request": request
        }
    )

@router.get("/login", response_class=HTMLResponse)
def show_login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": None
        }
    )

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        user = auth_controller.login(username=username, password=password)

        response = RedirectResponse(url="/applications", status_code=303)
        response.set_cookie(
            key="user_id",
            value=str(user.user_id),
            httponly=True,
            samesite="lax"
        )
        return response

    except ValueError as e:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": str(e)
            }
        )

@router.get("/register", response_class=HTMLResponse)
def show_register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "error": None
        }
    )

@router.post("/register")
def register(request: Request, name: str = Form(...), username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        auth_controller.register(name=name, username=username, email=email, password=password)

        return RedirectResponse(url="/login", status_code=303)

    except ValueError as e:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": str(e)
            }
        )

@router.post("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_id")
    return response
