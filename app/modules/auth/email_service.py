import logging

import boto3
from botocore.exceptions import ClientError

from app.core.config import Settings

logger = logging.getLogger(__name__)


class EmailService:
    """Thin wrapper around SES for transactional auth emails.

    Failures here are logged and swallowed rather than raised: Cognito has
    already dispatched its own code-delivery message by the time these are
    called, so a SES hiccup shouldn't fail the user-facing auth request.
    """

    def __init__(self, settings: Settings) -> None:
        self._client = boto3.client(
            "ses",
            region_name=settings.aws_region,
            endpoint_url=settings.aws_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        self._sender = settings.ses_sender_email

    def send_email(self, to: str, subject: str, html_body: str, text_body: str) -> None:
        try:
            self._client.send_email(
                Source=self._sender,
                Destination={"ToAddresses": [to]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                    },
                },
            )
        except ClientError:
            logger.exception("Failed to send SES email to %s", to)

    def send_password_reset_email(self, to: str, destination_hint: str) -> None:
        self.send_email(
            to=to,
            subject="Reset your my-farm password",
            html_body=(
                f"<p>We sent a password reset code to {destination_hint}. "
                "Enter it in the app to choose a new password. If you didn't "
                "request this, you can ignore this email.</p>"
            ),
            text_body=(
                f"We sent a password reset code to {destination_hint}. "
                "Enter it in the app to choose a new password. If you didn't "
                "request this, you can ignore this email."
            ),
        )

    def send_password_changed_email(self, to: str) -> None:
        self.send_email(
            to=to,
            subject="Your my-farm password was changed",
            html_body="<p>Your password was just changed. If this wasn't you, contact support immediately.</p>",
            text_body="Your password was just changed. If this wasn't you, contact support immediately.",
        )
