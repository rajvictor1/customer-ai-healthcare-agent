import re
from typing import Tuple
from app.models import Conversation, Message

class PolicyLayer:
    def apply(self, conversation: Conversation, user_text: str) -> Tuple[bool, str, str]:
        conv = conversation
        text = user_text

        # Healthcare guardrails
        if re.search(r"\b(diagnose|diagnosis|symptoms|pain|disease|tumor|cancer)\b", text, re.I):
            return True, "HEALTHCARE_MEDICAL", "I'm not a doctor and can't diagnose or interpret symptoms. For medical concerns, please contact your provider or call emergency services if it's urgent."
        if re.search(r"\b(lab results?|test results?|blood work|x-ray results?)\b", text, re.I):
            return True, "HEALTHCARE_RESULTS", "I can't interpret lab or imaging results. Please review them with your care team."

        # Authentication requirement for sensitive actions
        sensitive_intents = {"HC_REFILL", "HC_BILLING"}
        user_msg = conv.messages[-1] if conv.messages else None
        if user_msg and user_msg.role == "user" and user_msg.intent in sensitive_intents and not conv.context.get("authenticated"):
            return True, "AUTH_REQUIRED", "To proceed, I need to verify your identity. Please provide your 4-digit PIN or patient ID."

        return False, "", ""

    def looks_like_auth(self, text: str) -> bool:
        return bool(re.search(r"\b\d{4,10}\b", text))
