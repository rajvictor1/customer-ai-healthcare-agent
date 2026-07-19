import os
import re
import json
from typing import Tuple, Optional

# Lazy import OpenAI so the app starts without an API key
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

INTENT_PATTERNS = {
    "HC_APPOINTMENT": [r"book appointment", r"schedule", r"see a doctor", r"follow.?up", r"book.*with.*dr"],
    "HC_REFILL": [r"refill", r"prescription", r"medicine", r"medication"],
    "HC_BILLING": [r"copay", r"billing", r"insurance", r"invoice", r"payment"],
    "HC_PROVIDER": [r"find a doctor", r"provider", r"dermatologist", r"specialist", r"find.*dr"],
    "HC_INFO": [r"visiting hours", r"clinic hours", r"location", r"general info"],
}

SAFETY_PATTERNS = [
    (r"\bemergency\b|\bheart attack\b|\bstroke\b|\bcan.?t breathe\b|\bsuicide\b|\bkill myself\b", "SAFETY_EMERGENCY"),
    (r"my ssn\b|\bsocial security\b|\bpassword\b|\bcvv\b|\bcredit card number\b", "SAFETY_PII"),
]

ENTITY_PATTERNS = {
    "date": re.compile(r"\b(today|tomorrow|next\s+\w+|\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b", re.I),
    "provider": re.compile(r"\b(dr\.?\s+\w+|doctor\s+\w+|nurse\s+\w+)\b", re.I),
    "medication": re.compile(r"\b\w+pril\b|\b\w+sartan\b|\b\w+statin\b|\b\w+profen\b|\bmetformin\b|\binsulin\b|\blisinopril\b", re.I),
}


class IntentClassifier:
    def __init__(self, use_llm: bool = True, confidence_threshold: float = 0.75):
        self.use_llm = use_llm
        self.confidence_threshold = confidence_threshold

    def classify(self, text: str) -> Tuple[str, float]:
        if self.use_llm:
            llm_result = self._llm_classify(text)
            if llm_result:
                return llm_result[0], llm_result[1]

        text_lower = text.lower()
        best_intent = "UNKNOWN"
        best_score = 0.0
        best_match_len = 0
        for intent, patterns in INTENT_PATTERNS.items():
            for pat in patterns:
                match = re.search(pat, text_lower)
                if match:
                    # Prefer the most specific (longest) regex match when multiple intents match.
                    score = 0.85 + min(len(match.group(0)) / 100, 0.1)
                    if score > best_score or (score == best_score and len(match.group(0)) > best_match_len):
                        best_score = score
                        best_intent = intent
                        best_match_len = len(match.group(0))
        return best_intent, round(min(best_score, 0.98), 2)

    def _llm_classify(self, text: str) -> Optional[Tuple[str, float, dict]]:
        """Use OpenAI to classify intent and extract entities. Falls back to regex."""
        if not OpenAI or not os.environ.get("OPENAI_API_KEY"):
            return None

        domain = "healthcare"
        intent_examples = "\n".join([f"- {k}" for k in INTENT_PATTERNS.keys()])

        prompt = f"""Classify the user message for a {domain} customer support AI agent.
Return ONLY a JSON object with keys: intent, confidence (0.0-1.0), entities (object).

Allowed intents:
{intent_examples}

Message: {text}
"""
        try:
            client = OpenAI()
            resp = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            content = resp.choices[0].message.content
            if content is None:
                return None
            data = json.loads(content)
            intent = data.get("intent", "UNKNOWN")
            confidence = float(data.get("confidence", 0.0))
            if intent not in INTENT_PATTERNS and intent != "UNKNOWN":
                intent = "UNKNOWN"
            if confidence < self.confidence_threshold:
                return None
            return intent, round(min(confidence, 0.99), 2), data.get("entities", {})
        except Exception:
            return None

    def extract_entities(self, text: str) -> dict:
        # Regex entity extraction kept consistent regardless of LLM path.
        entities = {}
        for key, pat in ENTITY_PATTERNS.items():
            m = pat.search(text)
            if m:
                entities[key] = m.group(1).strip() if m.lastindex else m.group(0).strip()
        return entities

    def safety_check(self, text: str) -> Tuple[bool, Optional[str]]:
        for pat, reason in SAFETY_PATTERNS:
            if re.search(pat, text, re.I):
                return True, reason
        return False, None
