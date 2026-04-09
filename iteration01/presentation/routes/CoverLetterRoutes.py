from fastapi import APIRouter, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="presentation/templates")

# From main.py
cover_letter_controller = None

def get_current_user_id(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None

    try:
        return int(user_id)
    except ValueError:
        return None

@router.get("/cover_letters", response_class=HTMLResponse)
def show_cover_letters_page(request: Request, limit: int = 50, offset: int = 0, sort: str = "id", direction: str = "DESC"):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    cover_letters = cover_letter_controller.list_cover_letters(
        user_id=user_id,
        limit=limit,
        offset=offset,
        sort=sort,
        direction=direction
    )

    return templates.TemplateResponse(
        "cover_letters.html",
        {
            "request": request,
            "cover_letters": cover_letters
        }
    )

@router.get("/cover_letters/create", response_class=HTMLResponse)
def show_create_cover_letter_page(request: Request):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "create_cover_letter.html",
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
@router.post("/cover_letters/create")
async def create_cover_letter(request: Request, cover_letter_name: str = Form(...), file: UploadFile = File(...)):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        file_bytes = await file.read()

        cover_letter_controller.create_cover_letter(
            user_id=user_id,
            cover_letter_name=cover_letter_name,
            original_filename=file.filename,
            content_type=file.content_type,
            file_bytes=file_bytes
        )

        return RedirectResponse(url="/cover_letters", status_code=303)

    except ValueError as e:
        return templates.TemplateResponse(
            "create_cover_letter.html",
            {
                "request": request,
                "error": str(e)
            }
        )

@router.get("/cover_letters/{cover_letter_id}/download")
def download_cover_letter(request: Request, cover_letter_id: int):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        download_url = cover_letter_controller.get_cover_letter_download_url(
            cover_letter_id=cover_letter_id,
            user_id=user_id
        )

        return RedirectResponse(url=download_url, status_code=303)

    except ValueError:
        return RedirectResponse(url="/cover_letters", status_code=303)


@router.post("/cover_letters/{cover_letter_id}/delete")
def delete_resume(request: Request, cover_letter_id: int):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        cover_letter_controller.delete_cover_letter(
            cover_letter_id=cover_letter_id,
            user_id=user_id
        )

    except ValueError:
        pass

    return RedirectResponse(url="/cover_letters", status_code=303)
