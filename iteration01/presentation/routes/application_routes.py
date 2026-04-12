import json
import os
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from fastapi import APIRouter, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from business.application_status import ApplicationStatus

router = APIRouter()
templates = Jinja2Templates(directory="presentation/templates")

# From main.py
application_controller = None
resume_controller = None
cover_letter_controller = None


def get_geoapify_api_key():
    return os.getenv("GEOAPIFY_API_KEY")


US_STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia",
}


def normalize_country(country):
    if not country:
        return country
    if country == "United States of America":
        return "United States"
    return country


def expand_state_name(state, country):
    if not state:
        return state
    if normalize_country(country) == "United States" and len(state) == 2:
        return US_STATE_NAMES.get(state.upper(), state)
    return state


def parse_location_from_label(label):
    if not label:
        return None, None, None

    parts = [part.strip() for part in label.split(",") if part.strip()]
    if len(parts) < 3:
        return None, None, None

    country = normalize_country(parts[-1])
    state = parts[-2]
    city = parts[-3]

    state = state.split()[0] if any(char.isdigit() for char in state) else state
    state = expand_state_name(state, country)

    return city, state, country


def normalize_geoapify_feature(feature):
    properties = feature.get("properties", feature)
    geometry = feature.get("geometry", {})
    coordinates = geometry.get("coordinates", [properties.get("lon"), properties.get("lat")])

    city = (
        properties.get("city")
        or properties.get("town")
        or properties.get("village")
        or properties.get("suburb")
        or properties.get("municipality")
        or properties.get("county")
        or properties.get("state")
    )
    state = properties.get("state") or properties.get("state_code")
    country = normalize_country(properties.get("country"))
    label = properties.get("formatted") or ", ".join([part for part in [city, state, country] if part])
    fallback_city, fallback_state, fallback_country = parse_location_from_label(label)

    city = city or fallback_city
    state = expand_state_name(state or fallback_state, country or fallback_country)
    country = country or fallback_country
    compact_label = ", ".join([part for part in [city, state, country] if part])

    return {
        "label": compact_label or label,
        "full_label": label,
        "city": city,
        "state": state,
        "country": country,
        "lat": properties.get("lat") or (coordinates[1] if len(coordinates) > 1 else None),
        "lng": properties.get("lon") or (coordinates[0] if coordinates else None),
    }


def geoapify_request(endpoint, params):
    api_key = get_geoapify_api_key()
    if not api_key:
        raise ValueError("GEOAPIFY_API_KEY is not configured")

    query_string = urlencode({**params, "apiKey": api_key})
    url = f"https://api.geoapify.com/v1/geocode/{endpoint}?{query_string}"

    with urlopen(url, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))

def get_current_user_id(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None

    try:
        return int(user_id)
    except ValueError:
        return None


def normalize_optional_text(value):
    if value is None:
        return None
    value = value.strip()
    return value or None


def normalize_optional_int(value):
    if value is None:
        return None
    if isinstance(value, int):
        return value
    value = value.strip()
    return int(value) if value else None


def fallback_document_name(filename, explicit_name, default_label):
    explicit_name = normalize_optional_text(explicit_name)
    if explicit_name:
        return explicit_name
    if filename:
        return os.path.splitext(filename)[0]
    return default_label


def extract_created_id(created_value):
    if created_value is None:
        return None
    if isinstance(created_value, dict):
        return created_value.get("id")
    if isinstance(created_value, (tuple, list)):
        return created_value[0] if created_value else None
    return created_value

@router.get("/applications", response_class=HTMLResponse)
def show_applications_page(request: Request, limit: int = 50, offset: int = 0, sort: str = "id", direction: str = "DESC"):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    applications = application_controller.list_applications(
        user_id=user_id
    )

    return templates.TemplateResponse(
        request,
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

    resumes = resume_controller.list_resumes(user_id=user_id)
    cover_letters = cover_letter_controller.list_cover_letters(user_id=user_id)

    return templates.TemplateResponse(
        request,
        "create_application.html",
        {
            "request": request,
            "error": None,
            "date_applied": date.today().isoformat(),
            "job_country": "United States",
            "resumes": resumes,
            "cover_letters": cover_letters,
            "resume_mode": "existing" if resumes else "upload",
            "cover_letter_mode": "existing",
            "geoapify_enabled": bool(get_geoapify_api_key()),
        }
    )

@router.post("/applications/create")
async def create_application(
        request: Request,
        date_applied: str = Form(...),
        job_title: str = Form(...),
        job_company: str = Form(None),
        job_name: str = Form(None),
        job_description: str = Form(None),
        job_city: str = Form(None),
        job_state: str = Form(None),
        job_country: str = Form("United States"),
        hourly_rate: str = Form(None),
        salary_amount: str = Form(None),
        job_phone: str = Form(None),
        job_email: str = Form(None),
        resume_fk: str = Form(None),
        cover_letter_fk: str = Form(None),
        resume_mode: str = Form("existing"),
        resume_name: str = Form(None),
        resume_file: UploadFile = File(None),
        cover_letter_mode: str = Form("existing"),
        cover_letter_name: str = Form(None),
        cover_letter_file: UploadFile = File(None)
):

    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    resumes = resume_controller.list_resumes(user_id=user_id)
    cover_letters = cover_letter_controller.list_cover_letters(user_id=user_id)
    resume_mode = resume_mode or ("existing" if resumes else "upload")
    cover_letter_mode = cover_letter_mode or "existing"

    try:
        resume_fk_value = normalize_optional_int(resume_fk)
        cover_letter_fk_value = normalize_optional_int(cover_letter_fk)
        resume_mode = resume_mode.strip().lower()
        cover_letter_mode = cover_letter_mode.strip().lower()

        if resume_mode not in {"existing", "upload"}:
            raise ValueError("Resume selection mode is invalid")

        if cover_letter_mode not in {"existing", "upload"}:
            raise ValueError("Cover letter selection mode is invalid")

        if resume_mode == "upload":
            if resume_file is None or not resume_file.filename:
                raise ValueError("Resume is required. Choose an existing resume or upload a new one.")

            resume_bytes = await resume_file.read()
            created_resume = resume_controller.create_resume(
                user_id=user_id,
                resume_name=fallback_document_name(resume_file.filename, resume_name, "Resume"),
                original_filename=resume_file.filename,
                content_type=resume_file.content_type,
                file_bytes=resume_bytes
            )
            resume_fk_value = extract_created_id(created_resume)
        elif resume_fk_value is None:
            raise ValueError("Resume is required. Choose an existing resume or upload a new one.")

        if cover_letter_mode == "upload" and cover_letter_file is not None and cover_letter_file.filename:
            cover_letter_bytes = await cover_letter_file.read()
            created_cover_letter = cover_letter_controller.create_cover_letter(
                user_id=user_id,
                cover_letter_name=fallback_document_name(cover_letter_file.filename, cover_letter_name, "Cover Letter"),
                original_filename=cover_letter_file.filename,
                content_type=cover_letter_file.content_type,
                file_bytes=cover_letter_bytes
            )
            cover_letter_fk_value = extract_created_id(created_cover_letter)

        application_controller.create_application(
            user_id=user_id,
            date_applied=date_applied,
            job_title=job_title,
            job_company=job_company,
            job_name=job_name,
            job_description=job_description,
            job_city=job_city,
            job_state=job_state,
            job_country=job_country,
            hourly_rate=hourly_rate,
            salary_amount=salary_amount,
            job_phone=job_phone,
            job_email=job_email,
            resume_id=resume_fk_value,
            cover_letter_id=cover_letter_fk_value
        )

        return RedirectResponse(url="/applications", status_code=303)

    except ValueError as e:
        return templates.TemplateResponse(
            request,
            "create_application.html",
            {
                "request": request,
                "error": str(e),
                "date_applied": date_applied,
                "job_title": job_title,
                "job_company": job_company,
                "job_name": job_name,
                "job_description": job_description,
                "job_city": job_city,
                "job_state": job_state,
                "job_country": job_country,
                "hourly_rate": hourly_rate,
                "salary_amount": salary_amount,
                "job_phone": job_phone,
                "job_email": job_email,
                "resume_fk": resume_fk,
                "cover_letter_fk": cover_letter_fk,
                "resume_mode": resume_mode,
                "resume_name": resume_name,
                "cover_letter_mode": cover_letter_mode,
                "cover_letter_name": cover_letter_name,
                "resumes": resumes,
                "cover_letters": cover_letters,
                "geoapify_enabled": bool(get_geoapify_api_key()),
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
        request,
        "application_detail.html",
        {
            "request": request,
            "application": application,
            "error": None,
            "geoapify_enabled": bool(get_geoapify_api_key()),
        }
    )

@router.post("/applications/{app_id}/update")
def update_application(
        request: Request,
        app_id: int,
        date_applied: str = Form(None),
        job_title: str = Form(None),
        job_company: str = Form(None),
        job_name: str = Form(None),
        job_description: str = Form(None),
        job_city: str = Form(None),
        job_state: str = Form(None),
        job_country: str = Form(None),
        hourly_rate: str = Form(None),
        salary_amount: str = Form(None),
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
            job_city=job_city,
            job_state=job_state,
            job_country=job_country,
            hourly_rate=hourly_rate,
            salary_amount=salary_amount,
            job_phone=job_phone,
            job_email=job_email,
            resume_id=resume_fk,
            cover_letter_id=cover_letter_fk,
            job_status=job_status,
            date_applied=date_applied
        )

        return RedirectResponse(url=f"/applications/{app_id}", status_code=303)

    except ValueError as e:
        application = application_controller.get_application(app_id=app_id, user_id=user_id)

        return templates.TemplateResponse(
            request,
            "application_detail.html",
            {
                "request": request,
                "application": application,
                "error": str(e),
                "geoapify_enabled": bool(get_geoapify_api_key()),
            }
        )


@router.get("/api/locations/search")
def search_locations(query: str):
    if not query or len(query.strip()) < 2:
        return JSONResponse({"results": []})

    try:
        data = geoapify_request(
            "autocomplete",
            {
                "text": query.strip(),
                "limit": 6,
                "type": "city",
            },
        )
        results = [normalize_geoapify_feature(feature) for feature in data.get("features", data.get("results", []))]
        return JSONResponse({"results": results})
    except (ValueError, HTTPError, URLError, json.JSONDecodeError) as exc:
        return JSONResponse({"results": [], "error": str(exc)}, status_code=503)


@router.get("/api/locations/reverse")
def reverse_location(lat: float, lng: float):
    try:
        data = geoapify_request(
            "reverse",
            {
                "lat": lat,
                "lon": lng,
                "limit": 1,
            },
        )
        features = data.get("features", data.get("results", []))
        result = normalize_geoapify_feature(features[0]) if features else None
        return JSONResponse({"result": result})
    except (ValueError, HTTPError, URLError, json.JSONDecodeError) as exc:
        return JSONResponse({"result": None, "error": str(exc)}, status_code=503)


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


@router.post("/applications/{app_id}/status")
def update_application_status(request: Request, app_id: int, job_status: int = Form(...)):
    user_id = get_current_user_id(request)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        application_controller.set_status(
            app_id=app_id,
            user_id=user_id,
            job_status=ApplicationStatus(job_status),
        )
    except (ValueError, KeyError):
        pass

    return RedirectResponse(url="/applications", status_code=303)
