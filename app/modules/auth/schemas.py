from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None


class SignUpResponse(BaseModel):
    user_sub: str
    confirmed: bool
    delivery_medium: str | None = None
    destination: str | None = None


class ConfirmSignUpRequest(BaseModel):
    email: EmailStr
    confirmation_code: str


class ResendConfirmationRequest(BaseModel):
    email: EmailStr


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    id_token: str
    access_token: str
    refresh_token: str | None = None
    expires_in: int
    token_type: str


class RefreshTokenRequest(BaseModel):
    email: EmailStr
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    delivery_medium: str
    destination: str


class ConfirmForgotPasswordRequest(BaseModel):
    email: EmailStr
    confirmation_code: str
    new_password: str = Field(min_length=8)


class GoogleAuthorizeResponse(BaseModel):
    authorization_url: str
