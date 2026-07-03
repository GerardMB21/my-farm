import base64
import hashlib
import hmac
from urllib.parse import urlencode

import boto3
import httpx
from fastapi import HTTPException, status

from app.core.config import Settings
from app.modules.auth.email_service import EmailService
from app.modules.auth.exceptions import cognito_error_handler
from app.modules.auth.schemas import (
    ConfirmForgotPasswordRequest,
    ConfirmSignUpRequest,
    ForgotPasswordResponse,
    RefreshTokenRequest,
    SignInRequest,
    SignUpRequest,
    SignUpResponse,
    TokenResponse,
)


class AuthService:
    def __init__(self, settings: Settings, email_service: EmailService) -> None:
        self._settings = settings
        self._email_service = email_service
        self._client_id = settings.cognito_client_id
        self._client_secret = settings.cognito_client_secret
        self._idp = boto3.client(
            "cognito-idp",
            region_name=settings.aws_region,
            endpoint_url=settings.aws_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    def _secret_hash_kwargs(self, username: str) -> dict[str, str]:
        if not self._client_secret:
            return {}
        digest = hmac.new(
            self._client_secret.encode("utf-8"),
            (username + self._client_id).encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return {"SecretHash": base64.b64encode(digest).decode()}

    def _auth_parameters(self, **params: str) -> dict[str, str]:
        secret_hash = self._secret_hash_kwargs(params.get("USERNAME", ""))
        if secret_hash:
            params["SECRET_HASH"] = secret_hash["SecretHash"]
        return params

    @staticmethod
    def _token_response(auth_result: dict) -> TokenResponse:
        return TokenResponse(
            id_token=auth_result["IdToken"],
            access_token=auth_result["AccessToken"],
            refresh_token=auth_result.get("RefreshToken"),
            expires_in=auth_result["ExpiresIn"],
            token_type=auth_result["TokenType"],
        )

    @cognito_error_handler
    def sign_up(self, payload: SignUpRequest) -> SignUpResponse:
        user_attributes = [{"Name": "email", "Value": payload.email}]
        if payload.full_name:
            user_attributes.append({"Name": "name", "Value": payload.full_name})

        response = self._idp.sign_up(
            ClientId=self._client_id,
            Username=payload.email,
            Password=payload.password,
            UserAttributes=user_attributes,
            **self._secret_hash_kwargs(payload.email),
        )
        delivery = response.get("CodeDeliveryDetails") or {}
        return SignUpResponse(
            user_sub=response["UserSub"],
            confirmed=response["UserConfirmed"],
            delivery_medium=delivery.get("DeliveryMedium"),
            destination=delivery.get("Destination"),
        )

    @cognito_error_handler
    def confirm_sign_up(self, payload: ConfirmSignUpRequest) -> None:
        self._idp.confirm_sign_up(
            ClientId=self._client_id,
            Username=payload.email,
            ConfirmationCode=payload.confirmation_code,
            **self._secret_hash_kwargs(payload.email),
        )

    @cognito_error_handler
    def resend_confirmation_code(self, email: str) -> None:
        self._idp.resend_confirmation_code(
            ClientId=self._client_id,
            Username=email,
            **self._secret_hash_kwargs(email),
        )

    @cognito_error_handler
    def sign_in(self, payload: SignInRequest) -> TokenResponse:
        response = self._idp.initiate_auth(
            ClientId=self._client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters=self._auth_parameters(
                USERNAME=payload.email,
                PASSWORD=payload.password,
            ),
        )
        if "AuthenticationResult" not in response:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Additional challenge required: {response.get('ChallengeName')}",
            )
        return self._token_response(response["AuthenticationResult"])

    @cognito_error_handler
    def refresh_tokens(self, payload: RefreshTokenRequest) -> TokenResponse:
        response = self._idp.initiate_auth(
            ClientId=self._client_id,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters=self._auth_parameters(
                USERNAME=payload.email,
                REFRESH_TOKEN=payload.refresh_token,
            ),
        )
        token_response = self._token_response(response["AuthenticationResult"])
        token_response.refresh_token = payload.refresh_token
        return token_response

    @cognito_error_handler
    def forgot_password(self, email: str) -> ForgotPasswordResponse:
        response = self._idp.forgot_password(
            ClientId=self._client_id,
            Username=email,
            **self._secret_hash_kwargs(email),
        )
        delivery = response["CodeDeliveryDetails"]
        self._email_service.send_password_reset_email(to=email, destination_hint=delivery["Destination"])
        return ForgotPasswordResponse(
            delivery_medium=delivery["DeliveryMedium"],
            destination=delivery["Destination"],
        )

    @cognito_error_handler
    def confirm_forgot_password(self, payload: ConfirmForgotPasswordRequest) -> None:
        self._idp.confirm_forgot_password(
            ClientId=self._client_id,
            Username=payload.email,
            ConfirmationCode=payload.confirmation_code,
            Password=payload.new_password,
            **self._secret_hash_kwargs(payload.email),
        )
        self._email_service.send_password_changed_email(to=payload.email)

    # def get_google_authorize_url(self) -> str:
    #     params = {
    #         "identity_provider": "Google",
    #         "redirect_uri": self._settings.google_oauth_redirect_uri,
    #         "response_type": "code",
    #         "client_id": self._client_id,
    #         "scope": self._settings.google_oauth_scopes,
    #     }
    #     return f"https://{self._settings.cognito_domain}/oauth2/authorize?{urlencode(params)}"

    # async def exchange_google_code(self, code: str) -> TokenResponse:
    #     data = {
    #         "grant_type": "authorization_code",
    #         "client_id": self._client_id,
    #         "code": code,
    #         "redirect_uri": self._settings.google_oauth_redirect_uri,
    #     }
    #     auth = (self._client_id, self._client_secret) if self._client_secret else None

    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(
    #             f"https://{self._settings.cognito_domain}/oauth2/token",
    #             data=data,
    #             auth=auth,
    #             headers={"Content-Type": "application/x-www-form-urlencoded"},
    #         )

    #     if response.is_error:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google token exchange failed")

    #     payload = response.json()
    #     return TokenResponse(
    #         id_token=payload["id_token"],
    #         access_token=payload["access_token"],
    #         refresh_token=payload.get("refresh_token"),
    #         expires_in=payload["expires_in"],
    #         token_type=payload["token_type"],
    #     )
