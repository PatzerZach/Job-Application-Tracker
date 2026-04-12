from urllib.parse import quote, urlparse

from fastapi import APIRouter, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
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


def build_document_viewer_payload(request: Request, content_url: str, download_url: str, content_type: str | None):
    normalized_type = (content_type or "").lower()
    absolute_url = download_url

    if download_url.startswith("/"):
        absolute_url = f"{str(request.base_url).rstrip('/')}{download_url}"

    parsed = urlparse(absolute_url)
    is_public_remote = parsed.scheme in {"http", "https"} and parsed.hostname not in {"localhost", "127.0.0.1"}

    if normalized_type == "application/pdf":
        return {
            "viewer_mode": "pdf",
            "viewer_src": f"{content_url}#toolbar=0&navpanes=0&zoom=page-fit",
            "viewer_note": "Rendered directly in AppsTrackr for an in-browser review experience."
        }

    if normalized_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return {
            "viewer_mode": "docx",
            "viewer_src": content_url,
            "viewer_note": "Rendered directly inside AppsTrackr using a DOCX browser renderer."
        }

    if normalized_type == "application/msword" and is_public_remote:
        return {
            "viewer_mode": "office",
            "viewer_src": f"https://view.officeapps.live.com/op/embed.aspx?src={quote(absolute_url, safe='')}",
            "viewer_note": "Rendered inside AppsTrackr using Microsoft Office Web Viewer for classic Word document support."
        }

    return {
        "viewer_mode": "fallback",
        "viewer_src": content_url,
        "viewer_note": "This file type is available to open and download, but inline preview depends on the document format."
    }


def build_file_response(file_bytes: bytes, filename: str, content_type: str, download: bool = False):
    ascii_filename = filename.encode("ascii", "ignore").decode() or "document"
    ascii_filename = ascii_filename.replace('"', "")
    encoded_filename = quote(filename or "document", safe="")
    disposition = "attachment" if download else "inline"
    headers = {
        "Content-Disposition": f"{disposition}; filename=\"{ascii_filename}\"; filename*=UTF-8''{encoded_filename}",
        "Cache-Control": "private, max-age=300",
    }
    return Response(content=file_bytes, media_type=content_type or "application/octet-stream", headers=headers)

@router.get("/cover_letters", response_class=HTMLResponse)
def show_cover_letters_page(request: Request, limit: int = 50, offset: int = 0, sort: str = "id", direction: str = "DESC"):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    cover_letters = cover_letter_controller.list_cover_letters(
        user_id=user_id
    )

    return templates.TemplateResponse(
        request,
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
        request,
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
            request,
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


@router.get("/cover_letters/{cover_letter_id}/view")
def view_cover_letter(request: Request, cover_letter_id: int):
    user_id = get_current_user_id(request)
    if user_id is None:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    try:
        cover_letter = cover_letter_controller.get_cover_letter(
            user_id=user_id,
            cover_letter_id=cover_letter_id
        )

        if cover_letter is None:
            return JSONResponse({"error": "Cover letter not found"}, status_code=404)

        download_url = cover_letter_controller.get_cover_letter_download_url(
            user_id=user_id,
            cover_letter_id=cover_letter_id
        )
        content_url = str(request.url_for("cover_letter_content", cover_letter_id=cover_letter_id))

        viewer = build_document_viewer_payload(request, content_url, download_url, cover_letter.content_type)

        return JSONResponse(
            {
                "viewer_mode": viewer["viewer_mode"],
                "viewer_src": viewer["viewer_src"],
                "viewer_note": viewer["viewer_note"],
                "content_url": content_url,
                "document_open_url": content_url,
                "document_download_url": f"{content_url}?download=true",
                "document_external_url": download_url,
                "content_type": cover_letter.content_type,
            }
        )

    except ValueError:
        return JSONResponse({"error": "Cover letter not found"}, status_code=404)


@router.get("/cover_letters/{cover_letter_id}/content", name="cover_letter_content")
def cover_letter_content(request: Request, cover_letter_id: int, download: bool = False):
    user_id = get_current_user_id(request)
    if user_id is None:
        return Response(status_code=401)

    try:
        payload = cover_letter_controller.get_cover_letter_file(
            user_id=user_id,
            cover_letter_id=cover_letter_id
        )

        return build_file_response(
            file_bytes=payload["file_bytes"],
            filename=payload["original_filename"],
            content_type=payload["content_type"],
            download=download
        )
    except ValueError:
        return Response(status_code=404)


@router.post("/cover_letters/{cover_letter_id}/delete")
def delete_cover_letter(request: Request, cover_letter_id: int):
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
