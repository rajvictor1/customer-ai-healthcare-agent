# Codex Deployment Notes — Make It Production Ready

## Repositories

- **E-Commerce:** https://github.com/rajvictor1/customer-ai-ecommerce-agent
- **Healthcare:** https://github.com/rajvictor1/customer-ai-healthcare-agent

Both repos are already productionized with:
- FastAPI backend
- Jinja2 frontend (chat + admin)
- SQLite persistence (change to PostgreSQL for production)
- OpenAI LLM fallback intent classification
- Docker + docker-compose
- Auth stub (OAuth2/OIDC ready)
- Twilio WhatsApp adapter stub
- Tests + pytest
- Deploy guides in `deploy/`
- Domain-specific PRD in `PRD.md`

## Your 5-step deployment task

### Step 1 — Push the CI workflow

The GitHub Actions workflow file `.github/workflows/ci.yml` exists locally but was not pushed due to OAuth scope limits. Run this first on each repo:

```bash
git clone https://github.com/rajvictor1/customer-ai-ecommerce-agent.git
cd customer-ai-ecommerce-agent
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow"
git push origin main
```

Then do the same for `customer-ai-healthcare-agent`.

### Step 2 — Add real environment variables

Copy `.env.example` to `.env` and fill in real values:

```bash
cp .env.example .env
```

Required keys:

```text
DATABASE_URL=sqlite:///data/conversations.db   # or postgresql://user:pass@host/db
SECRET_KEY=<generate a strong random key>
OPENAI_API_KEY=<your OpenAI API key>
OPENAI_MODEL=gpt-4o-mini
AUTH_ISSUER=<your OAuth/OIDC issuer>
AUTH_CLIENT_ID=<your OAuth client ID>
AUTH_CLIENT_SECRET=<your OAuth client secret>
TWILIO_ACCOUNT_SID=<Twilio SID>
TWILIO_AUTH_TOKEN=<Twilio token>
TWILIO_WHATSAPP_NUMBER=<Twilio WhatsApp number>
LOG_LEVEL=INFO
```

For local dev, you only need `SECRET_KEY`. OpenAI key enables LLM classification. Twilio enables real WhatsApp replies.

### Step 3 — Replace stubs with real integrations

| File | What to replace |
|---|---|
| `app/auth.py` | Stub `get_current_user` with real OAuth2/OIDC token validation (Auth0, Keycloak, Azure AD, patient portal SSO). |
| `app/backend_mock.py` | Mock data with real API clients: OMS for e-commerce, EHR/scheduling/pharmacy/billing for healthcare. |
| `app/whatsapp.py` | Already calls Twilio SDK if credentials are set. Verify webhook URL in Twilio console. |

Keep the existing function signatures so the rest of the app continues to work.

### Step 4 — Switch to PostgreSQL (recommended for production)

1. Add `asyncpg` and `sqlalchemy` or use `databases` + `psycopg2` to `requirements.txt`.
2. Replace `app/store.py` SQLite logic with PostgreSQL.
3. Use `DATABASE_URL=postgresql://...` in `.env`.
4. Add Alembic migrations.

Alternatively, keep SQLite for the first deploy and migrate later.

### Step 5 — Deploy

Choose one platform from `deploy/`:

**Easiest — Render or Fly.io:**

```bash
# Render
# - Create Web Service, connect repo, set env vars, start command: uvicorn run:app --host 0.0.0.0 --port 10000

# Fly.io
fly launch --now
fly secrets set DATABASE_URL=... OPENAI_API_KEY=... TWILIO_ACCOUNT_SID=... TWILIO_AUTH_TOKEN=... TWILIO_WHATSAPP_NUMBER=...
fly deploy
```

**Cloud — AWS/GCP/Azure:**

See `deploy/aws.md`, `deploy/gcp.md`, `deploy/azure.md`.

## Post-deploy verification

Run these checks:

```bash
curl https://your-domain/api/health
curl -X POST https://your-domain/api/chat   -H "Content-Type: application/json"   -d '{"message":"Where is my order","customer_id":"cust_456","channel":"web"}'
```

For WhatsApp, configure Twilio webhook URL to `https://your-domain/api/webhook/whatsapp`.

## Compliance notes

- **Healthcare:** Do not enable PHI integrations until HIPAA BAA is signed with all vendors.
- **E-Commerce:** Never capture raw card data in the bot. Redirect payments to PCI-compliant hosted checkout.

## Files you should read first

1. `README.md` — run instructions
2. `PRD.md` — product requirements
3. `CODEX_HANDOFF.md` — full productionization roadmap
4. `deploy/<your-platform>.md` — platform-specific deploy steps
