import hashlib
import json
import logging
import re
import secrets
from datetime import timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from business.user import User
from dal.common import DALConflict
from dal.db import connect
from dal.users_q import (
    create_auth_token,
    create_user,
    delete_user_account,
    delete_user_applications,
    delete_user_cover_letters,
    delete_user_resumes,
    get_auth_token,
    get_user,
    get_user_by_email,
    get_user_by_identifier,
    get_user_by_username,
    mark_auth_token_used,
    mark_user_email_verified,
    update_user_email,
    update_user_password,
)
from dal.resumes_q import list_resumes_by_user
from dal.cover_letters_q import list_cover_letters_by_user


EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
)
USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_-]{3,32}$")
logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db_path, resend_api_key=None, email_from=None, storage_service=None):
        self.db_path = db_path
        self.resend_api_key = resend_api_key
        self.email_from = email_from or "AppsTrackr <appstrackr@appstrackr.com>"
        self.storage_service = storage_service
        self.password_hasher = PasswordHasher(
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            salt_len=16,
        )

    def hash_password(self, password):
        password = self.validate_password(password)
        return self.password_hasher.hash(password)

    def verify_password(self, password, stored_hash):
        try:
            return self.password_hasher.verify(stored_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    def validate_name(self, name):
        if not isinstance(name, str):
            raise ValueError("Name must be a string")

        name = " ".join(name.strip().split())
        if len(name) < 2:
            raise ValueError("Please enter your full name")

        return name

    def validate_username(self, username):
        if not isinstance(username, str):
            raise ValueError("Username must be a string")

        username = username.strip()
        if not USERNAME_REGEX.fullmatch(username):
            raise ValueError("Username must be 3-32 characters and use only letters, numbers, underscores, or hyphens")

        return username

    def validate_password(self, password):
        if not isinstance(password, str):
            raise ValueError("Password must be a string")

        password = password.strip()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        return password

    def verify_email(self, email):
        if not isinstance(email, str):
            raise ValueError("Email must be a string")

        email = email.strip().lower()

        if not email:
            raise ValueError("Email cannot be empty")

        if not EMAIL_REGEX.fullmatch(email):
            raise ValueError("Enter a valid email address")

        local_part, domain = email.split("@", 1)
        if local_part.startswith(".") or local_part.endswith(".") or ".." in local_part:
            raise ValueError("Enter a valid email address")

        if domain.startswith(".") or domain.endswith(".") or ".." in domain:
            raise ValueError("Enter a valid email address")

        labels = domain.split(".")
        if len(labels) < 2 or any(not label or label.startswith("-") or label.endswith("-") for label in labels):
            raise ValueError("Enter a valid email address")

        if len(labels[-1]) < 2:
            raise ValueError("Enter a valid email address")

        return email

    def ensure_matching_emails(self, email, confirm_email):
        normalized_email = self.verify_email(email)
        normalized_confirm = self.verify_email(confirm_email)

        if normalized_email != normalized_confirm:
            raise ValueError("Email addresses do not match")

        return normalized_email

    def ensure_matching_passwords(self, password, confirm_password):
        normalized_password = self.validate_password(password)
        normalized_confirm = self.validate_password(confirm_password)

        if normalized_password != normalized_confirm:
            raise ValueError("Passwords do not match")

        return normalized_password

    def _build_user(self, row):
        if row is None:
            return None

        return User(
            user_id=row["id"],
            name=row["name"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password"],
            is_verified=bool(row.get("is_verified", False)),
            email_verified_at=row.get("email_verified_at"),
        )

    def _hash_token(self, token):
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _issue_token(self, conn, user_id, token_type, lifetime):
        token = secrets.token_urlsafe(32)
        create_auth_token(
            conn=conn,
            user_id=user_id,
            token_hash=self._hash_token(token),
            token_type=token_type,
            expires_at=self._future_timestamp(lifetime),
        )
        return token

    def _future_timestamp(self, lifetime):
        from datetime import datetime, timezone

        return datetime.now(timezone.utc) + lifetime

    def _build_link(self, base_url, path, token):
        base_url = (base_url or "").rstrip("/")
        if not base_url:
            raise ValueError("The application base URL is required to send account emails")

        return f"{base_url}{path}?token={quote(token, safe='')}"

    def _send_email(self, to_email, subject, html):
        if not self.resend_api_key:
            raise ValueError("Email delivery is not configured. Add RESEND_API_KEY to your environment.")

        payload = {
            "from": self.email_from,
            "to": [to_email],
            "subject": subject,
            "html": html,
        }
        request = Request(
            "https://api.resend.com/emails",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.resend_api_key}",
                "Content-Type": "application/json",
                "User-Agent": "AppsTrackr/1.0",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=15) as response:
                response.read()
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            raise ValueError(f"Unable to send account email right now. {details or exc.reason}") from exc
        except URLError as exc:
            raise ValueError("Unable to reach the email service right now. Please try again.") from exc

    def _verification_email_html(self, user_name, verify_link):
        first_name = (user_name or "there").split(" ")[0]
        return f"""
        <div style="background:#0a0a12;padding:32px 18px;font-family:Arial,sans-serif;color:#eeedf0;">
          <div style="max-width:620px;margin:0 auto;background:#13132a;border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:36px;">
            <div style="display:inline-block;padding:8px 14px;border-radius:999px;background:rgba(240,200,74,0.12);border:1px solid rgba(240,200,74,0.32);color:#f0c84a;font-size:12px;letter-spacing:0.08em;text-transform:uppercase;">AppsTrackr</div>
            <h1 style="font-size:32px;line-height:1.1;margin:18px 0 14px;">Verify your email</h1>
            <p style="font-size:16px;line-height:1.7;color:#c4c2d7;margin:0 0 18px;">Hi {first_name}, welcome to AppsTrackr. Confirm your email address to activate secure account recovery and keep your account settings protected.</p>
            <a href="{verify_link}" style="display:inline-block;background:#f0c84a;color:#0a0a12;text-decoration:none;font-weight:700;padding:14px 22px;border-radius:14px;margin:8px 0 18px;">Verify Email</a>
            <p style="font-size:14px;line-height:1.7;color:#8e8ca8;margin:0 0 8px;">This verification link expires in 7 days.</p>
            <p style="font-size:14px;line-height:1.7;color:#8e8ca8;margin:0;">If the button does not work, copy this link into your browser:<br><span style="word-break:break-all;color:#eeedf0;">{verify_link}</span></p>
          </div>
        </div>
        """

    def _password_reset_email_html(self, user_name, reset_link):
        first_name = (user_name or "there").split(" ")[0]
        return f"""
        <div style="background:#0a0a12;padding:32px 18px;font-family:Arial,sans-serif;color:#eeedf0;">
          <div style="max-width:620px;margin:0 auto;background:#13132a;border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:36px;">
            <div style="display:inline-block;padding:8px 14px;border-radius:999px;background:rgba(240,200,74,0.12);border:1px solid rgba(240,200,74,0.32);color:#f0c84a;font-size:12px;letter-spacing:0.08em;text-transform:uppercase;">AppsTrackr</div>
            <h1 style="font-size:32px;line-height:1.1;margin:18px 0 14px;">Reset your password</h1>
            <p style="font-size:16px;line-height:1.7;color:#c4c2d7;margin:0 0 18px;">Hi {first_name}, we received a request to reset your AppsTrackr password. Use the secure link below to choose a new one.</p>
            <a href="{reset_link}" style="display:inline-block;background:#f0c84a;color:#0a0a12;text-decoration:none;font-weight:700;padding:14px 22px;border-radius:14px;margin:8px 0 18px;">Reset Password</a>
            <p style="font-size:14px;line-height:1.7;color:#8e8ca8;margin:0 0 8px;">This reset link expires in 1 hour.</p>
            <p style="font-size:14px;line-height:1.7;color:#8e8ca8;margin:0;">If you did not request this, you can safely ignore this email.</p>
          </div>
        </div>
        """

    def _password_changed_email_html(self, user_name, forgot_password_link):
        first_name = (user_name or "there").split(" ")[0]
        forgot_password_link = forgot_password_link or ""
        action_block = (
            f'<a href="{forgot_password_link}" style="display:inline-block;background:#f0c84a;color:#0a0a12;text-decoration:none;font-weight:700;padding:14px 22px;border-radius:14px;margin:8px 0 18px;">Secure Your Account</a>'
            if forgot_password_link else ""
        )
        return f"""
        <div style="background:#0a0a12;padding:32px 18px;font-family:Arial,sans-serif;color:#eeedf0;">
          <div style="max-width:620px;margin:0 auto;background:#13132a;border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:36px;">
            <div style="display:inline-block;padding:8px 14px;border-radius:999px;background:rgba(240,200,74,0.12);border:1px solid rgba(240,200,74,0.32);color:#f0c84a;font-size:12px;letter-spacing:0.08em;text-transform:uppercase;">AppsTrackr Security</div>
            <h1 style="font-size:32px;line-height:1.1;margin:18px 0 14px;">Your password was changed</h1>
            <p style="font-size:16px;line-height:1.7;color:#c4c2d7;margin:0 0 18px;">Hi {first_name}, this is a confirmation that your AppsTrackr password was just updated.</p>
            <p style="font-size:14px;line-height:1.7;color:#8e8ca8;margin:0 0 8px;">If this was you, no further action is needed.</p>
            <p style="font-size:14px;line-height:1.7;color:#8e8ca8;margin:0 0 18px;">If this was not you, secure the account immediately by resetting the password again.</p>
            {action_block}
          </div>
        </div>
        """

    def register(self, name, username, password, email, confirm_email, base_url):
        name = self.validate_name(name)
        username = self.validate_username(username)
        password_hash = self.hash_password(password)
        normalized_email = self.ensure_matching_emails(email, confirm_email)

        with connect(self.db_path) as conn:
            if get_user_by_username(conn, username):
                raise ValueError("Username already exists")

            if get_user_by_email(conn, normalized_email):
                raise ValueError("Email already exists")

            try:
                user_id = create_user(conn, name, username, password_hash, normalized_email)
            except DALConflict as exc:
                raise ValueError("An account with that username or email already exists") from exc

            token = self._issue_token(conn, user_id, "verify_email", timedelta(days=7))
            verify_link = self._build_link(base_url, "/verify-email", token)
            self._send_email(
                normalized_email,
                "Verify your AppsTrackr email",
                self._verification_email_html(name, verify_link),
            )

        return user_id

    def login(self, identifier, password):
        if not identifier or not password:
            raise ValueError("Username/email and password are required")

        identifier = identifier.strip()
        password = password.strip()

        with connect(self.db_path) as conn:
            row = get_user_by_identifier(conn, identifier)

            if row is None:
                raise ValueError("Username/email or password is incorrect")

            stored_hash = row["password"]
            if not self.verify_password(password, stored_hash):
                raise ValueError("Username/email or password is incorrect")

            return self._build_user(row)

    def request_password_reset(self, email, base_url):
        normalized_email = self.verify_email(email)

        with connect(self.db_path) as conn:
            row = get_user_by_email(conn, normalized_email)
            if row is None:
                return False

            token = self._issue_token(conn, row["id"], "reset_password", timedelta(hours=1))
            reset_link = self._build_link(base_url, "/reset-password", token)
            self._send_email(
                normalized_email,
                "Reset your AppsTrackr password",
                self._password_reset_email_html(row["name"], reset_link),
            )
            return True

    def verify_email_token(self, token):
        if not token:
            raise ValueError("Verification link is invalid or has expired")

        with connect(self.db_path) as conn:
            row = get_auth_token(conn, self._hash_token(token), "verify_email")
            if row is None:
                raise ValueError("Verification link is invalid or has expired")

            mark_user_email_verified(conn, row["user_fk"])
            mark_auth_token_used(conn, row["token_id"])
            return self._build_user(row)

    def resend_verification(self, user_id, base_url):
        with connect(self.db_path) as conn:
            row = get_user(conn, user_id)
            if row is None:
                raise ValueError("User does not exist")

            if not row.get("email"):
                raise ValueError("Add an email address before requesting verification")

            if row.get("is_verified"):
                raise ValueError("Your email is already verified")

            token = self._issue_token(conn, row["id"], "verify_email", timedelta(days=7))
            verify_link = self._build_link(base_url, "/verify-email", token)
            self._send_email(
                row["email"],
                "Verify your AppsTrackr email",
                self._verification_email_html(row["name"], verify_link),
            )

        return True

    def reset_password(self, token, password, confirm_password, base_url):
        password = self.ensure_matching_passwords(password, confirm_password)

        if not token:
            raise ValueError("Reset link is invalid or has expired")

        with connect(self.db_path) as conn:
            row = get_auth_token(conn, self._hash_token(token), "reset_password")
            if row is None:
                logger.warning("Reset password failed because the token was invalid or expired.")
                raise ValueError("Reset link is invalid or has expired")

            update_user_password(conn, row["user_fk"], self.hash_password(password))
            mark_auth_token_used(conn, row["token_id"])
            updated_row = get_user(conn, row["user_fk"])
            if updated_row is None or not self.verify_password(password, updated_row["password"]):
                logger.error("Password reset did not persist for user_id=%s", row["user_fk"])
                raise ValueError("We couldn't save your new password. Please try again.")

        if row.get("email"):
            fresh_reset_token = None
            with connect(self.db_path) as conn:
                fresh_reset_token = self._issue_token(conn, row["user_fk"], "reset_password", timedelta(hours=1))

            self._send_email(
                row["email"],
                "Your AppsTrackr password was changed",
                self._password_changed_email_html(
                    row["name"],
                    self._build_link(base_url, "/reset-password", fresh_reset_token),
                ),
            )
        return True

    def change_password(self, user_id, current_password, new_password, confirm_password, base_url):
        new_password = self.ensure_matching_passwords(new_password, confirm_password)

        with connect(self.db_path) as conn:
            row = get_user(conn, user_id)
            if row is None:
                logger.warning("Password change failed because user_id=%s does not exist", user_id)
                raise ValueError("User does not exist")

            current_password_matches = self.verify_password((current_password or "").strip(), row["password"])
            if not current_password_matches:
                logger.warning("Password change rejected for user_id=%s because the current password did not verify", user_id)
                raise ValueError("Your current password is incorrect")

            if self.verify_password(new_password, row["password"]):
                logger.info("Password change rejected for user_id=%s because the new password matched the old password", user_id)
                raise ValueError("Choose a new password that is different from your current one")

            update_user_password(conn, user_id, self.hash_password(new_password))
            recovery_token = None
            if row.get("email"):
                recovery_token = self._issue_token(conn, row["id"], "reset_password", timedelta(hours=1))
            updated_row = get_user(conn, user_id)
            if updated_row is None or not self.verify_password(new_password, updated_row["password"]):
                logger.error("Password change did not persist for user_id=%s", user_id)
                raise ValueError("We couldn't save your new password. Please try again.")

        if row.get("email"):
            self._send_email(
                row["email"],
                "Your AppsTrackr password was changed",
                self._password_changed_email_html(
                    row["name"],
                    self._build_link(base_url, "/reset-password", recovery_token),
                ),
            )
        logger.info("Password change completed for user_id=%s", user_id)
        return True

    def change_email(self, user_id, email, confirm_email, base_url):
        normalized_email = self.ensure_matching_emails(email, confirm_email)

        with connect(self.db_path) as conn:
            row = get_user(conn, user_id)
            if row is None:
                raise ValueError("User does not exist")

            current_email = (row.get("email") or "").strip().lower()
            if current_email == normalized_email:
                raise ValueError("That is already your current email address")

            existing_user = get_user_by_email(conn, normalized_email)
            if existing_user and existing_user["id"] != user_id:
                raise ValueError("Email already exists")

            try:
                update_user_email(conn, user_id, normalized_email)
            except DALConflict as exc:
                raise ValueError("Email already exists") from exc

            token = self._issue_token(conn, user_id, "verify_email", timedelta(days=7))
            verify_link = self._build_link(base_url, "/verify-email", token)
            self._send_email(
                normalized_email,
                "Verify your new AppsTrackr email",
                self._verification_email_html(row["name"], verify_link),
            )

        return normalized_email

    def delete_account(self, user_id, current_password):
        current_password = (current_password or "").strip()
        if not current_password:
            raise ValueError("Enter your current password to delete your account")

        resume_paths = []
        cover_letter_paths = []

        with connect(self.db_path) as conn:
            row = get_user(conn, user_id)
            if row is None:
                raise ValueError("User does not exist")

            if not self.verify_password(current_password, row["password"]):
                logger.warning("Account deletion rejected for user_id=%s because the current password did not verify", user_id)
                raise ValueError("Your current password is incorrect")

            resume_paths = [
                resume["storage_path"]
                for resume in list_resumes_by_user(conn, user_id, limit=5000, offset=0, sort="id", direction="DESC")
                if resume.get("storage_path")
            ]
            cover_letter_paths = [
                cover_letter["storage_path"]
                for cover_letter in list_cover_letters_by_user(conn, user_id, limit=5000, offset=0, sort="id", direction="DESC")
                if cover_letter.get("storage_path")
            ]

            delete_user_applications(conn, user_id)
            delete_user_resumes(conn, user_id)
            delete_user_cover_letters(conn, user_id)
            delete_user_account(conn, user_id)

        if self.storage_service:
            for storage_path in resume_paths:
                try:
                    self.storage_service.delete_file(bucket_name="resumes", storage_path=storage_path)
                except Exception as exc:
                    logger.warning("Failed to delete resume storage object for user_id=%s path=%s: %s", user_id, storage_path, exc)

            for storage_path in cover_letter_paths:
                try:
                    self.storage_service.delete_file(bucket_name="cover_letters", storage_path=storage_path)
                except Exception as exc:
                    logger.warning("Failed to delete cover letter storage object for user_id=%s path=%s: %s", user_id, storage_path, exc)

        logger.info("Account deletion completed for user_id=%s", user_id)
        return True

    def get_user_by_id(self, user_id):
        if not user_id:
            raise ValueError("User does not exist")

        with connect(self.db_path) as conn:
            row = get_user(conn, user_id)
            if row is None:
                raise ValueError("User does not exist")

            return self._build_user(row)
