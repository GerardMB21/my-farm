import functools
import logging
from collections.abc import Callable
from typing import NoReturn, TypeVar

from botocore.exceptions import ClientError
from fastapi import HTTPException, status
from typing_extensions import ParamSpec

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")

_ERROR_STATUS_MAP: dict[str, int] = {
    "UsernameExistsException": status.HTTP_409_CONFLICT,
    "NotAuthorizedException": status.HTTP_401_UNAUTHORIZED,
    "UserNotFoundException": status.HTTP_404_NOT_FOUND,
    "UserNotConfirmedException": status.HTTP_403_FORBIDDEN,
    "CodeMismatchException": status.HTTP_400_BAD_REQUEST,
    "ExpiredCodeException": status.HTTP_400_BAD_REQUEST,
    "InvalidPasswordException": status.HTTP_422_UNPROCESSABLE_CONTENT,
    "InvalidParameterException": status.HTTP_422_UNPROCESSABLE_CONTENT,
    "AliasExistsException": status.HTTP_409_CONFLICT,
    "LimitExceededException": status.HTTP_429_TOO_MANY_REQUESTS,
    "TooManyRequestsException": status.HTTP_429_TOO_MANY_REQUESTS,
    "TooManyFailedAttemptsException": status.HTTP_429_TOO_MANY_REQUESTS,
}


def raise_for_cognito_error(error: ClientError) -> NoReturn:
    code = error.response["Error"]["Code"]
    message = error.response["Error"].get("Message", code)
    status_code = _ERROR_STATUS_MAP.get(code, status.HTTP_400_BAD_REQUEST)
    raise HTTPException(status_code=status_code, detail=message) from error


def cognito_error_handler(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except ClientError as error:
            raise_for_cognito_error(error)

    return wrapper
