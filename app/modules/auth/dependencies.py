from functools import lru_cache

from app.core.config import get_settings
from app.modules.auth.email_service import EmailService
from app.modules.auth.service import AuthService


@lru_cache
def get_email_service() -> EmailService:
    return EmailService(get_settings())


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService(get_settings(), get_email_service())
