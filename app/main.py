from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from app.models import IncomingEvent
from app.router import handle_event
from app.store import STORE
from app.config import get_settings
from app.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(title="Healthcare AI Agent MVP")
templates = Jinja2Templates(directory="templates")

class ChatMessage(BaseModel):
    message: str
    customer_id: str
    channel: str = "web"
    conversation_id: Optional[str] = None


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("http_request", method=request.method, path=request.url.path)
    response = await call_next(request)
    return response

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "chat.html")

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    conversations = STORE.list_recent(hours=48)
    escalated_count = sum(1 for c in conversations if c.status == "escalated")
    healthcare_count = sum(1 for c in conversations if c.domain == "healthcare")
    return templates.TemplateResponse(request, "admin.html", {
        "conversations": conversations,
        "escalated_count": escalated_count,
        "healthcare_count": healthcare_count,
    })

@app.post("/api/chat")
async def chat(req: ChatMessage):
    logger.info("chat_request", customer_id=req.customer_id, channel=req.channel)
    event = IncomingEvent(
        channel=req.channel,
        customer_id=req.customer_id,
        domain="healthcare",
        message=req.message,
        metadata={"conversation_id": req.conversation_id},
    )
    return await handle_event(event)

@app.post("/api/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    phone = form.get("From", "anon")
    body = form.get("Body", "")
    event = IncomingEvent(
        channel="whatsapp",
        customer_id=phone,
        domain="healthcare",
        message=body,
    )
    result = await handle_event(event)
    return {"reply": result["response"]}

@app.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    conv = STORE.db["conversations"].get(conversation_id)
    if not conv:
        return JSONResponse({"error": "not found"}, status_code=404)
    return dict(conv)

@app.get("/api/health")
def health():
    return {"status": "ok"}

import os
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
