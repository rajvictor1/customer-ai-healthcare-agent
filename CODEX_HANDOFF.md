# Codex Handoff — Build & Deploy Customer-Facing AI Agent

## Goal

Take the two MVP repositories below and build production-ready, deployable customer-facing AI agents.

- **E-Commerce:** https://github.com/rajvictor1/customer-ai-ecommerce-agent
- **Healthcare:** https://github.com/rajvictor1/customer-ai-healthcare-agent

Both repos currently contain a working FastAPI MVP with regex-based intent classification, mock backend, SQLite persistence, and a Jinja2 web UI. Your job is to evolve them into real AI agents with actual NLU, authentication, integrations, and deployment.

---

## Current MVP State

Each repo contains:

```text
├── PRD.md                 # Full product requirements document
├── README.md              # Domain-specific run instructions
├── requirements.txt       # Dependencies
├── run.py                 # Uvicorn entrypoint
├── app/
│   ├── __init__.py
│   ├── models.py          # Pydantic models
│   ├── classifier.py      # Regex intent + entity + safety classifier
│   ├── policy.py          # Guardrails and auth rules
│   ├── response_engine.py # Response generation
│   ├── backend_mock.py    # Mock OMS / EHR / scheduling data
│   ├── router.py          # Conversation orchestration
│   ├── store.py           # SQLite persistence
│   └── main.py            # FastAPI routes + Jinja2 UI
└── templates/
    ├── chat.html          # Web chat UI
    └── admin.html         # Admin dashboard
```

### How to run locally

```bash
cd customer-ai-ecommerce-agent   # or customer-ai-healthcare-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn run:app --reload --port 8001   # ecommerce
uvicorn run:app --reload --port 8002   # healthcare
```

Open:
- Chat UI: `http://localhost:8001/` or `http://localhost:8002/`
- Admin: `http://localhost:8001/admin` or `http://localhost:8002/admin`
- Health: `http://localhost:8001/api/health`

---

## Known Sandbox Limitations to Fix First

1. **SQLite path is `/tmp/`**
   - In `app/store.py`, change:
     ```python
     DB_PATH = "/tmp/customer_ai_ecommerce_conversations.db"
     # or
     DB_PATH = "/tmp/customer_ai_healthcare_conversations.db"
     ```
   - To:
     ```python
     DB_PATH = "data/conversations.db"
     ```
   - Ensure the `data/` directory is created on startup.

2. **No real authentication**
   - E-commerce currently auto-authenticates for order tracking.
   - Healthcare uses a fake 4-digit PIN step-up.
   - Replace with real identity provider (OAuth2 / OIDC / patient portal SSO).

3. **Regex-based NLU**
   - Replace with a real LLM or fine-tuned classifier.
   - Keep the existing `IntentClassifier` interface so other modules don't break.

4. **Mock backend only**
   - Replace `backend_mock.py` with real API clients.

---

## Phase 1 — Stabilize & Harden (Do This First)

### 1.1 Environment & Configuration

- Add `.env.example` and load config with `pydantic-settings`.
- Required env vars:
  ```text
  DATABASE_URL=sqlite:///data/conversations.db
  SECRET_KEY=<generate strong random key>
  OPENAI_API_KEY=<or other LLM provider>
  AUTH_ISSUER=<OIDC issuer>
  AUTH_CLIENT_ID=<client id>
  AUTH_CLIENT_SECRET=<client secret>
  OMS_API_URL=<e-commerce order management system>
  EHR_API_URL=<healthcare EHR FHIR base URL>
  TWILIO_ACCOUNT_SID=<for WhatsApp>
  TWILIO_AUTH_TOKEN=<for WhatsApp>
  TWILIO_WHATSAPP_NUMBER=<sandbox or production number>
  ```
- Add Docker + `docker-compose.yml` for local PostgreSQL and Redis.
- Switch SQLite to PostgreSQL for production.
- Add Alembic migrations.

### 1.2 Logging, Observability, Tests

- Add structured logging (`structlog`).
- Add OpenTelemetry or basic request/response middleware.
- Add unit tests with `pytest` for:
  - classifier
  - policy layer
  - response engine
  - router / API routes
- Add integration tests for `/api/chat`, `/admin`, `/api/webhook/whatsapp`.
- Add pre-commit hooks (`ruff`, `black`, `mypy`).

### 1.3 Security Baseline

- Add HTTPS-only cookie settings.
- Add CORS policy tied to known origins.
- Add rate limiting (`slowapi` or custom middleware).
- Sanitize all user input before logging.
- Hash/mask PII in logs.
- Use `python-jose` or Authlib for token validation.

---

## Phase 2 — Replace Regex NLU with Real AI

### 2.1 Intent Classification

- Use OpenAI GPT-4o-mini / Claude 3.5 Haiku or a fine-tuned model.
- Expected JSON output:
  ```json
  {
    "intent": "EC_ORDER_TRACK",
    "confidence": 0.97,
    "entities": {"order_id": "10001"},
    "language": "en"
  }
  ```
- Fall back to regex classifier if LLM is unavailable or confidence < 0.8.
- Add multi-turn slot filling for missing entities.

### 2.2 Response Generation

- Replace hardcoded responses with LLM-generated answers grounded by:
  - RAG over an approved knowledge base.
  - Tool results from backend APIs.
- Use system prompts with guardrails.
- Add response caching for common answers.

### 2.3 Safety Layer

- Use a dedicated safety classifier or LLM moderation API.
- Keep hard-coded escalation rules for emergencies, PII, diagnosis requests, and explicit agent handoff phrases.
- Add PII/PHI detection and redaction before logging or model context.

---

## Phase 3 — Real Integrations

### E-Commerce (`customer-ai-ecommerce-agent`)

| Replace | With |
|---|---|
| `backend_mock.py` orders | Real OMS API (Shopify, Magento, custom) |
| `backend_mock.py` returns | Returns management service / RMA API |
| `backend_mock.py` search | Catalog search (Algolia, Elasticsearch) |
| `backend_mock.py` promos | Promotion / coupon service |
| Auth auto-flag | OAuth2 / customer account login |
| Channel default domain | Customer lookup by phone/email to set domain |

### Healthcare (`customer-ai-healthcare-agent`)

| Replace | With |
|---|---|
| `backend_mock.py` patients | EHR FHIR API (Epic, Cerner, custom) under BAA |
| `backend_mock.py` appointments | Scheduling system API |
| `backend_mock.py` refills | Pharmacy API (Surescripts / covered entity) |
| `backend_mock.py` billing | Billing/insurance eligibility API |
| `backend_mock.py` providers | Provider directory API |
| PIN step-up | Patient portal SSO + MFA (Epic MyChart, Auth0, etc.) |

---

## Phase 4 — Channels

### 4.1 Web Chat

- Keep current Jinja2 templates or replace with React/Vue widget.
- Add WebSocket support for real-time messages.
- Add file upload (prescriptions, return photos) with virus scanning.

### 4.2 WhatsApp

- Integrate Twilio WhatsApp Business API.
- Map `From` phone number to customer identity.
- Respect WhatsApp 24-hour session window rules.
- Implement opt-in / opt-out.

### 4.3 Phone / Voice (Optional)

- Add Twilio `<Gather>` + `<Say>` flow.
- Use Deepgram/Whisper for STT and ElevenLabs/Azure for TTS.
- DTMF for sensitive input.

### 4.4 Email (Optional)

- Add SendGrid / AWS SES inbound parsing.
- Thread-aware grouping.

### 4.5 In-App (Optional)

- Provide REST/websocket API for mobile SDK.

---

## Phase 5 — Deployment

### 5.1 Containerize

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 Cloud Deployment Options

| Platform | Steps |
|---|---|
| **Render / Railway / Fly.io** | Connect GitHub repo, set env vars, deploy |
| **AWS ECS / EKS** | Build image → ECR → ECS service with ALB |
| **GCP Cloud Run** | Build image → Artifact Registry → Cloud Run service |
| **Azure Container Apps** | Build image → ACR → Container App |

### 5.3 Production Checklist

- [ ] Use managed PostgreSQL (RDS, Cloud SQL, etc.)
- [ ] Use managed Redis for session/cache (ElastiCache, Memorystore)
- [ ] TLS termination at load balancer
- [ ] Secrets in AWS Secrets Manager / GCP Secret Manager / Azure Key Vault
- [ ] CI/CD via GitHub Actions
- [ ] Health checks at `/api/health`
- [ ] Graceful shutdown handling
- [ ] Database backups
- [ ] HIPAA BAA signed (healthcare) before any PHI integration
- [ ] PCI-DSS scope review (e-commerce) before any payment handling

---

## Phase 6 — Admin Dashboard Improvements

- Add filters: date range, status, intent, channel.
- Add conversation replay view.
- Add human takeover button that pauses the bot.
- Add CSAT feedback collection.
- Add intent accuracy / containment rate charts.
- Add content management for approved responses.

---

## Suggested First Pull Request for Codex

**Title:** `chore: harden MVP for production — config, DB, tests, Docker`

Scope:
1. Move SQLite path to `data/conversations.db`.
2. Add `.env.example` and `pydantic-settings`.
3. Add `docker-compose.yml` with PostgreSQL.
4. Add `pytest` + sample tests.
5. Add `ruff` / `black` / `mypy` pre-commit config.
6. Update `README.md` with new run instructions.

After that, tackle per-phase PRs:
- `feat: replace regex classifier with LLM`
- `feat: integrate real OMS/EHR APIs`
- `feat: add Twilio WhatsApp channel`
- `feat: add admin dashboard filters and analytics`
- `chore: containerize and add GitHub Actions CI/CD`

---

## Domain-Specific Notes

### Healthcare

- **Never allow diagnosis, symptom interpretation, or lab result reading.**
- Escalate any emergency language immediately.
- Require verified patient identity + MFA for refill/billing.
- Log every access to PHI; no plaintext PHI in logs.
- Ensure all third parties sign BAA.

### E-Commerce

- Never capture raw card data in the bot.
- Redirect payment disputes to hosted checkout or secure support.
- Authenticate order lookup against customer account.
- Mask PII in logs.

---

## Success Metrics to Track

- Bot containment rate ≥ 70%
- First-contact resolution ≥ 70%
- CSAT ≥ 4.2 / 5
- Intent accuracy ≥ 90%
- p95 response latency < 1.5s
- 0 PHI/PII incidents

---

## Support Files

Both repos include `PRD.md` with full requirements. Use it as the source of truth for scope, KPIs, compliance, and roadmap.
