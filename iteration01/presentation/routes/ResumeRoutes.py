from fastapi import APIRouter, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="presentation/templates")

# From main.py
resume_controller = None

def get_current_user_id(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None

    try:
        return int(user_id)
    except ValueError:
        return None

@router.get("/resumes", response_class=HTMLResponse)
def show_resumes_page(request: Request, limit: int = 50, offset: int = 0, sort: str = "id", direction: str = "DESC"):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    resumes = resume_controller.list_resumes(
        user_id=user_id,
        limit=limit,
        offset=offset,
        sort=sort,
        direction=direction
    )

    return templates.TemplateResponse(
        "resumes.html",
        {
            "request": request,
            "resumes": resumes
        }
    )

@router.get("/resumes/create", response_class=HTMLResponse)
def show_create_resume_page(request: Request):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "create_resume.html",
        {
            "request": request,
            "error": None
        }
    )

# Because I am using await with file.read() we need to make this function async
# Without async we would sit and run this until it is done.
# But with async and await, we are waiting while reading the file, but we arent
# blocking other logic, it doesnt stop here and wait, it can continue executing
# other code
@router.post("/resumes/create")
async def create_resume(request: Request, resume_name: str = Form(...), file: UploadFile = File(...)):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        file_bytes = await file.read()

        resume_controller.create_resume(
            user_id=user_id,
            resume_name=resume_name,
            original_filename=file.filename,
            content_type=file.content_type,
            file_bytes=file_bytes
        )

        return RedirectResponse(url="/resumes", status_code=303)

    except ValueError as e:
        return templates.TemplateResponse(
            "create_resume.html",
            {
                "request": request,
                "error": str(e)
            }
        )

@router.get("/resumes/{resume_id}/download")
def download_resume(request: Request, resume_id: int):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        download_url = resume_controller.get_resume_download_url(
            resume_id=resume_id,
            user_id=user_id
        )

        return RedirectResponse(url=download_url, status_code=303)

    except ValueError:
        return RedirectResponse(url="/resumes", status_code=303)


@router.post("/resumes/{resume_id}/delete")
def delete_resume(request: Request, resume_id: int):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        resume_controller.delete_resume(
            resume_id=resume_id,
            user_id=user_id
        )

    except ValueError:
        pass

    return RedirectResponse(url="/resumes", status_code=303)
