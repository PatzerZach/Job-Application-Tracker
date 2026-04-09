from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from iteration01.business import cover_letter

router = APIRouter()
templates = Jinja2Templates(directory="presentation/templates")

# From main.py
application_controller = None

def get_current_user_id(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None

    try:
        return int(user_id)
    except ValueError:
        return None

@router.get("/applications", response_class=HTMLResponse)
def show_applications_page(request: Request, limit: int = 50, offset: int = 0, sort: str = "id", direction: str = "DESC"):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    applications = application_controller.list_applications(
        user_id=user_id,
        limit=limit,
        offset=offset,
        sort=sort,
        direction=direction
    )

    return templates.TemplateResponse(
        "applications.html",
        {
            "request": request,
            "applications": applications,

        },
    )

@router.get("/applications/create", response_class=HTMLResponse)
def show_create_application_page(request: Request):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "create_application.html",
        {
            "request": request,
            "error": None
        }
    )

@router.post("/applications/create")
def create_application(
        request: Request,
        job_title: str = Form(...),
        job_company: str = Form(None),
        job_name: str = Form(None),
        job_description: str = Form(None),
        job_phone: str = Form(None),
        job_email: str = Form(None),
        resume_fk: int = Form(None),
        cover_letter_fk: int = Form(None)
):

    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        application_controller.create_application(
            user_id=user_id,
            job_title=job_title,
            company=job_company,
            job_name=job_name,
            description=job_description,
            phone=job_phone,
            email=job_email,
            resume_id=resume_fk,
            cover_letter_id=cover_letter_fk
        )

        return RedirectResponse(url="/applications", status_code=303)

    except ValueError as e:
        return templates.TemplateResponse(
            "create_application.html",
            {
                "request": request,
                "error": str(e)
            }
        )


@router.get("/applications/{app_id}", response_class=HTMLResponse)
def show_application_detail(request: Request, app_id: int):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    application = application_controller.get_application(
        app_id=app_id,
        user_id=user_id
    )

    if application is None:
        return RedirectResponse(url="/applications", status_code=303)

    return templates.TemplateResponse(
        "application_detail.html",
        {
            "request": request,
            "application": application,
            "error": None
        }
    )

@router.post("/applications/{app_id}/update")
def update_application(
        request: Request,
        app_id: int,
        job_title: str = Form(None),
        job_company: str = Form(None),
        job_name: str = Form(None),
        job_description: str = Form(None),
        job_phone: str = Form(None),
        job_email: str = Form(None),
        resume_fk: int = Form(None),
        cover_letter_fk: int = Form(None),
        job_status: int = Form(None)
):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        application_controller.update_application(
            app_id=app_id,
            user_id=user_id,
            job_title=job_title,
            job_company=job_company,
            job_name=job_name,
            job_description=job_description,
            job_phone=job_phone,
            job_email=job_email,
            resume_fk=resume_fk,
            cover_letter_fk=cover_letter_fk,
            job_status=job_status
        )

        return RedirectResponse(url=f"/applications/{app_id}", status_code=303)

    except ValueError as e:
        application = application_controller.get_application(app_id=app_id, user_id=user_id)

        return templates.TemplateResponse(
            "application_detail.html",
            {
                "request": request,
                "application": application,
                "error": str(e)
            }
        )


@router.post("/application/{app_id}/delete")
def delete_application(request: Request, app_id: int):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        application_controller.delete_application(app_id=app_id, user_id=user_id)
    except ValueError:
        pass

    return RedirectResponse(url="/applications", status_code=303)
