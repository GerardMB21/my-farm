from fastapi import APIRouter, Depends, Query, status
from fastapi.concurrency import run_in_threadpool

from app.modules.auth import schemas
from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sign-up", response_model=schemas.SignUpResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    payload: schemas.SignUpRequest,
    service: AuthService = Depends(get_auth_service),
) -> schemas.SignUpResponse:
    return await run_in_threadpool(service.sign_up, payload)


@router.post("/confirm-sign-up", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_sign_up(
    payload: schemas.ConfirmSignUpRequest,
    service: AuthService = Depends(get_auth_service),
) -> None:
    await run_in_threadpool(service.confirm_sign_up, payload)


@router.post("/resend-confirmation", status_code=status.HTTP_204_NO_CONTENT)
async def resend_confirmation(
    payload: schemas.ResendConfirmationRequest,
    service: AuthService = Depends(get_auth_service),
) -> None:
    await run_in_threadpool(service.resend_confirmation_code, payload.email)


@router.post("/sign-in", response_model=schemas.TokenResponse)
async def sign_in(
    payload: schemas.SignInRequest,
    service: AuthService = Depends(get_auth_service),
) -> schemas.TokenResponse:
    return await run_in_threadpool(service.sign_in, payload)


@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh(
    payload: schemas.RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> schemas.TokenResponse:
    return await run_in_threadpool(service.refresh_tokens, payload)


@router.post("/forgot-password", response_model=schemas.ForgotPasswordResponse)
async def forgot_password(
    payload: schemas.ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),
) -> schemas.ForgotPasswordResponse:
    return await run_in_threadpool(service.forgot_password, payload.email)


@router.post("/confirm-forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_forgot_password(
    payload: schemas.ConfirmForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),
) -> None:
    await run_in_threadpool(service.confirm_forgot_password, payload)


# @router.get("/google/login", response_model=schemas.GoogleAuthorizeResponse)
# async def google_login(
#     service: AuthService = Depends(get_auth_service),
# ) -> schemas.GoogleAuthorizeResponse:
#     return schemas.GoogleAuthorizeResponse(authorization_url=service.get_google_authorize_url())


# @router.get("/google/callback", response_model=schemas.TokenResponse)
# async def google_callback(
#     code: str = Query(...),
#     service: AuthService = Depends(get_auth_service),
# ) -> schemas.TokenResponse:
#     return await service.exchange_google_code(code)
