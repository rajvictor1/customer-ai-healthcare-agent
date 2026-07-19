from datetime import datetime
from typing import Dict, Any
from app.models import Conversation
from app.policy import PolicyLayer
from app.classifier import IntentClassifier
from app.response_engine import ENGINE
from app.store import STORE

classifier = IntentClassifier()
policy = PolicyLayer()

async def handle_event(event) -> Dict[str, Any]:
    conversation_id = event.metadata.get("conversation_id") or f"conv_{event.customer_id}"
    conv = STORE.get_or_create(conversation_id, event.customer_id, event.channel, event.domain)

    # 1. Safety check
    is_unsafe, safety_reason = classifier.safety_check(event.message)
    if is_unsafe:
        conv.status = "escalated"
        reply_text = "I'm transferring you to a human specialist right away because this requires personal attention."
        conv.messages.append(make_msg(event.message, "user", event.channel, intent="SAFETY"))
        conv.messages.append(make_msg(reply_text, "bot", event.channel, intent="SAFETY", escalated=True))
        conv.context["escalation_reason"] = safety_reason
        STORE.save(conv)
        return _format_response(conv, "SAFETY", reply_text)

    # 2. Classify intent + extract entities
    intent, confidence = classifier.classify(event.message)
    entities = classifier.extract_entities(event.message)

    # 3. Append user message
    conv.messages.append(make_msg(event.message, "user", event.channel, intent=intent, confidence=confidence))

    # 4. Apply policy guardrails / auth
    blocked, policy_reason, policy_reply = policy.apply(conv, event.message)
    if blocked:
        conv.messages.append(make_msg(policy_reply, "bot", event.channel, intent=policy_reason))
        STORE.save(conv)
        return _format_response(conv, policy_reason, policy_reply)

    # 5. Auth continuation: if previous bot message asked for PIN, treat digits as auth and re-process original intent
    if (len(conv.messages) >= 2 and conv.messages[-2].role == "bot" and
        conv.messages[-2].intent == "AUTH_REQUIRED"):
        conv.context["authenticated"] = True
        # Find the original user message before the AUTH_REQUIRED bot message
        original_msg = conv.messages[-3] if len(conv.messages) >= 3 else conv.messages[-1]
        intent = original_msg.intent or intent
        entities = classifier.extract_entities(original_msg.content)
        # Remove the temporary PIN message so policy and response remain clean
        conv.messages = conv.messages[:-1]
    else:
        # Ensure first-time sensitive intents still hit the AUTH_REQUIRED branch
        pass

    # 6. Generate response
    reply_text = ENGINE.generate(conv, intent, entities)
    conv.messages.append(make_msg(reply_text, "bot", event.channel, intent=intent))

    # 7. Confidence fallback
    if confidence < 0.75 and intent != "UNKNOWN":
        reply_text += "\n\nIf I didn't understand correctly, type 'talk to agent' to speak with a human."
        conv.messages[-1].content = reply_text

    # 8. Escalation phrase
    if "talk to agent" in event.message.lower() or "human" in event.message.lower():
        conv.status = "escalated"
        conv.messages[-1].escalated = True
        reply_text = "I'm connecting you to a live agent now. Please hold."
        conv.messages[-1].content = reply_text

    STORE.save(conv)
    return _format_response(conv, intent, reply_text)

def make_msg(content, role, channel, intent=None, confidence=None, escalated=False):
    from app.models import Message
    return Message(role=role, content=content, channel=channel, timestamp=datetime.utcnow(), intent=intent, confidence=confidence, escalated=escalated)

def _format_response(conv, intent, response) -> Dict[str, Any]:
    return {
        "conversation_id": conv.id,
        "response": response,
        "intent": intent,
        "status": conv.status,
        "channel": conv.channel,
    }
