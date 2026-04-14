from urllib.parse import urlencode

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="presentation/templates")

auth_controller = None


def get_current_user_id(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None

    try:
        return int(user_id)
    except ValueError:
        return None


def get_current_user(request: Request):
    user_id = get_current_user_id(request)
    if user_id is None:
        return None

    try:
        return auth_controller.get_user(user_id)
    except ValueError:
        return None


def get_base_url(request: Request):
    return str(request.base_url).rstrip("/")


def with_query(path, **params):
    filtered = {key: value for key, value in params.items() if value}
    if not filtered:
        return path

    return f"{path}?{urlencode(filtered)}"


def render_login(request: Request, error=None, success=None, info=None, identifier=""):
    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "request": request,
            "error": error,
            "success": success,
            "info": info,
            "identifier": identifier,
        },
    )


def render_register(request: Request, error=None, success=None, name="", username="", email="", confirm_email=""):
    return templates.TemplateResponse(
        request,
        "register.html",
        {
            "request": request,
            "error": error,
            "success": success,
            "name": name,
            "username": username,
            "email": email,
            "confirm_email": confirm_email,
        },
    )


def render_forgot_password(request: Request, error=None, success=None, email=""):
    return templates.TemplateResponse(
        request,
        "forgot_password.html",
        {
            "request": request,
            "error": error,
            "success": success,
            "email": email,
        },
    )


def render_reset_password(request: Request, token="", error=None, success=None):
    return templates.TemplateResponse(
        request,
        "reset_password.html",
        {
            "request": request,
            "token": token,
            "error": error,
            "success": success,
        },
    )


def render_profile(
    request: Request,
    user,
    success=None,
    info=None,
    error=None,
    password_error=None,
    email_error=None,
    delete_error=None,
    email_value=None,
    confirm_email_value=None,
):
    return templates.TemplateResponse(
        request,
        "profile.html",
        {
            "request": request,
            "user": user,
            "success": success,
            "info": info,
            "error": error,
            "password_error": password_error,
            "email_error": email_error,
            "delete_error": delete_error,
            "email_value": email_value,
            "confirm_email_value": confirm_email_value,
        },
    )


def apply_auth_cookies(response, user):
    response.set_cookie(
        key="user_id",
        value=str(user.user_id),
        httponly=True,
        samesite="lax"
    )
    response.set_cookie(
        key="username",
        value=user.username,
        httponly=False,
        samesite="lax"
    )
    response.set_cookie(
        key="is_verified",
        value="true" if user.is_verified else "false",
        httponly=False,
        samesite="lax"
    )
    return response


@router.get("/", response_class=HTMLResponse)
def show_landing_page(request: Request):
    return templates.TemplateResponse(
        request,
        "landing.html",
        {
            "request": request
        }
    )


@router.get("/login", response_class=HTMLResponse)
def show_login_page(
    request: Request,
    success: str | None = Query(default=None),
    info: str | None = Query(default=None),
    error: str | None = Query(default=None),
):
    return render_login(request, error=error, success=success, info=info)


@router.post("/login")
def login(request: Request, identifier: str = Form(...), password: str = Form(...)):
    try:
        user = auth_controller.login(identifier=identifier, password=password)

        response = RedirectResponse(url="/applications", status_code=303)
        return apply_auth_cookies(response, user)

    except ValueError as e:
        return render_login(request, error=str(e), identifier=identifier)


@router.get("/register", response_class=HTMLResponse)
def show_register_page(request: Request):
    return render_register(request)


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    confirm_email: str = Form(...),
    password: str = Form(...),
):
    try:
        auth_controller.register(
            name=name,
            username=username,
            email=email,
            confirm_email=confirm_email,
            password=password,
            base_url=get_base_url(request),
        )

        return RedirectResponse(
            url=with_query("/login", success="Account created. Check your email to verify your address."),
            status_code=303,
        )

    except ValueError as e:
        return render_register(
            request,
            error=str(e),
            name=name,
            username=username,
            email=email,
            confirm_email=confirm_email,
        )


@router.get("/forgot-password", response_class=HTMLResponse)
def show_forgot_password_page(request: Request):
    return render_forgot_password(request)


@router.post("/forgot-password")
def forgot_password(request: Request, email: str = Form(...)):
    try:
        auth_controller.request_password_reset(email=email, base_url=get_base_url(request))
        return render_forgot_password(
            request,
            success="If that email is in AppsTrackr, a reset link is on its way.",
        )
    except ValueError as e:
        return render_forgot_password(request, error=str(e), email=email)


@router.get("/reset-password", response_class=HTMLResponse)
def show_reset_password_page(request: Request, token: str | None = Query(default=None)):
    if not token:
        return RedirectResponse(url=with_query("/login", error="That reset link is invalid or has expired."), status_code=303)

    return render_reset_password(request, token=token)


@router.post("/reset-password")
def reset_password(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    try:
        auth_controller.reset_password(
            token=token,
            password=password,
            confirm_password=confirm_password,
            base_url=get_base_url(request),
        )
        return RedirectResponse(
            url=with_query("/login", success="Your password has been updated. Please sign in."),
            status_code=303,
        )
    except ValueError as e:
        return render_reset_password(request, token=token, error=str(e))


@router.get("/verify-email")
def verify_email(request: Request, token: str = Query(...)):
    try:
        user = auth_controller.verify_email_token(token)
        response = RedirectResponse(
            url=with_query("/login", success="Your email has been verified. You are ready to go."),
            status_code=303,
        )
        response.set_cookie(
            key="is_verified",
            value="true",
            httponly=False,
            samesite="lax"
        )
        if request.cookies.get("user_id") == str(user.user_id):
            response.set_cookie(
                key="username",
                value=user.username,
                httponly=False,
                samesite="lax"
            )
        return response
    except ValueError as e:
        return RedirectResponse(url=with_query("/login", error=str(e)), status_code=303)


@router.get("/profile", response_class=HTMLResponse)
def show_profile_page(
    request: Request,
    success: str | None = Query(default=None),
    info: str | None = Query(default=None),
    error: str | None = Query(default=None),
):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)

    return render_profile(request, user=user, success=success, info=info, error=error)


@router.post("/profile/password")
def update_profile_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        auth_controller.change_password(
            user_id=user.user_id,
            current_password=current_password,
            new_password=new_password,
            confirm_password=confirm_password,
            base_url=get_base_url(request),
        )
        response = RedirectResponse(
            url=with_query(
                "/login",
                success="Your password has been updated. Please sign in again with your new password.",
                info="We also sent a security email so you can recover the account quickly if that change was not yours. Check spam or junk if you do not see it right away.",
            ),
            status_code=303,
        )
        response.delete_cookie("user_id")
        response.delete_cookie("username")
        response.delete_cookie("is_verified")
        return response
    except ValueError as e:
        fresh_user = auth_controller.get_user(user.user_id)
        return render_profile(request, user=fresh_user, password_error=str(e))


@router.post("/profile/email")
def update_profile_email(
    request: Request,
    email: str = Form(...),
    confirm_email: str = Form(...),
):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        auth_controller.change_email(
            user_id=user.user_id,
            email=email,
            confirm_email=confirm_email,
            base_url=get_base_url(request),
        )
        response = RedirectResponse(
            url=with_query(
                "/profile",
                success="Your email was updated. Check your inbox to verify the new address.",
                info="We sent a fresh verification email to your new address.",
            ),
            status_code=303,
        )
        response.set_cookie(
            key="is_verified",
            value="false",
            httponly=False,
            samesite="lax"
        )
        return response
    except ValueError as e:
        fresh_user = auth_controller.get_user(user.user_id)
        return render_profile(
            request,
            user=fresh_user,
            email_error=str(e),
            email_value=email,
            confirm_email_value=confirm_email,
        )


@router.post("/profile/delete")
def delete_profile_account(
    request: Request,
    current_password: str = Form(...),
):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        auth_controller.delete_account(user.user_id, current_password)
        response = RedirectResponse(
            url=with_query(
                "/login",
                success="Your account has been deleted.",
                info="All of your AppsTrackr applications and stored documents were removed.",
            ),
            status_code=303,
        )
        response.delete_cookie("user_id")
        response.delete_cookie("username")
        response.delete_cookie("is_verified")
        return response
    except ValueError as e:
        fresh_user = auth_controller.get_user(user.user_id)
        return render_profile(request, user=fresh_user, delete_error=str(e))


@router.post("/profile/resend-verification")
def resend_verification(request: Request):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)

    try:
        auth_controller.resend_verification(user.user_id, get_base_url(request))
        return RedirectResponse(
            url=with_query("/profile", success="We sent a new verification email."),
            status_code=303,
        )
    except ValueError as e:
        fresh_user = auth_controller.get_user(user.user_id)
        return render_profile(request, user=fresh_user, error=str(e))


@router.post("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_id")
    response.delete_cookie("username")
    response.delete_cookie("is_verified")
    return response
