"""Twilio WhatsApp adapter.

Production: replace mock/stub calls with real Twilio SDK calls.
"""

from fastapi import Request

try:
    from twilio.rest import Client
except ImportError:
    Client = None

from app.config import get_settings
from app.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class WhatsAppAdapter:
    def __init__(self):
        self.client = None
        if Client and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    async def parse_incoming(self, request: Request) -> dict:
        form = await request.form()
        return {
            "from": form.get("From", "anon"),
            "to": form.get("To", settings.TWILIO_WHATSAPP_NUMBER),
            "body": form.get("Body", ""),
            "profile_name": form.get("ProfileName", ""),
        }

    def send_reply(self, to: str, body: str):
        """Send a WhatsApp reply. Stub unless Twilio is configured."""
        if self.client:
            try:
                self.client.messages.create(
                    from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                    body=body,
                    to=to,
                )
                logger.info("whatsapp_reply_sent", to=to)
            except Exception as e:
                logger.error("whatsapp_reply_failed", to=to, error=str(e))
        else:
            logger.info("whatsapp_reply_stub", to=to, body=body)


WHATSAPP = WhatsAppAdapter()
