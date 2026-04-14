import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from business.auth_service import AuthService
from business.application_service import ApplicationService
from business.resume_service import ResumeService
from business.cover_letter_service import CoverLetterService

from business.local_storage_service import LocalStorageService
from business.supabase_storage_service import SupabaseStorageService

from presentation.controllers.auth_controller import AuthController
from presentation.controllers.application_controller import ApplicationController
from presentation.controllers.resume_controller import ResumeController
from presentation.controllers.cover_letter_controller import CoverLetterController

from presentation.routes import auth_routes
from presentation.routes import application_routes
from presentation.routes import resume_routes
from presentation.routes import cover_letter_routes


load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="presentation/static"), name="static")


def build_storage_service():
    storage_backend = os.getenv("STORAGE_BACKEND", "local").lower()

    if storage_backend == "supabase":
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY are required when STORAGE_BACKEND=supabase")

        return SupabaseStorageService(
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )

    return LocalStorageService(base_dir="uploads")


def build_app():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL is required")

    storage_service = build_storage_service()

    # Services
    auth_service = AuthService(
        db_url,
        resend_api_key=os.getenv("RESEND_API_KEY"),
        email_from=os.getenv("EMAIL_FROM"),
        storage_service=storage_service
    )
    application_service = ApplicationService(db_url)
    resume_service = ResumeService(db_url, storage_service)
    cover_letter_service = CoverLetterService(db_url, storage_service)

    # Controllers
    auth_controller = AuthController(auth_service)
    application_controller = ApplicationController(application_service)
    resume_controller = ResumeController(resume_service)
    cover_letter_controller = CoverLetterController(cover_letter_service)

    # Inject controllers into route modules
    auth_routes.auth_controller = auth_controller
    application_routes.application_controller = application_controller
    application_routes.resume_controller = resume_controller
    application_routes.cover_letter_controller = cover_letter_controller
    resume_routes.resume_controller = resume_controller
    cover_letter_routes.cover_letter_controller = cover_letter_controller

    # Register routes
    app.include_router(auth_routes.router)
    app.include_router(application_routes.router)
    app.include_router(resume_routes.router)
    app.include_router(cover_letter_routes.router)


build_app()
