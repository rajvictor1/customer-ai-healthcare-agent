# Healthcare Customer-Facing AI Agent — MVP

Self-contained FastAPI MVP for healthcare patient support: appointment booking, prescription refills, billing/insurance, provider search, general info.

Includes HIPAA-aware guardrails: no diagnosis, no lab interpretation, emergency escalation, and PIN step-up for sensitive intents.

## Run

```bash
cd /Users/mac/customer-ai-healthcare-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn run:app --reload --port 8002
```

Open `http://localhost:8002` for chat and `http://localhost:8002/admin` for the dashboard.

## Files

- `app/main.py` — FastAPI routes + web UI.
- `app/router.py` — conversation orchestration with PIN auth continuation.
- `app/classifier.py` — intent/entity/safety classifier (HC intents only).
- `app/policy.py` — healthcare guardrails and PIN step-up policy.
- `app/response_engine.py` — response generation for healthcare.
- `app/backend_mock.py` — mock EHR, providers, appointments, billing.
- `app/store.py` — SQLite persistence.
- `app/models.py` — Pydantic models.
- `templates/` — Jinja2 chat + admin templates.
- `requirements.txt` — dependencies.

## Supported intents

| Intent | Example |
|---|---|
| HC_APPOINTMENT | "Book a follow-up with Dr. Sharma" |
| HC_REFILL | "Refill my Lisinopril" |
| HC_BILLING | "What is my copay for next visit?" |
| HC_PROVIDER | "Find a dermatologist near Munger" |
| HC_INFO | "What are your visiting hours?" |

## Safety rules

- Refuses to diagnose or interpret symptoms.
- Refuses to read lab/imaging results.
- Escalates emergency phrases (e.g., "heart attack") immediately.
- Requires 4-digit PIN / patient ID for prescription refills and billing.

## Notes

This is a local MVP. Production needs real NLU, patient portal SSO/MFA, EHR integration under BAA, HIPAA-compliant logging, and secure secrets management.

## Production Deployment

1. Copy `.env.example` to `.env` and fill in real credentials.
2. Run with Docker:
   ```bash
   docker-compose up --build
   ```
3. Or deploy to Render / Fly.io / AWS / GCP / Azure using guides in `deploy/`.
4. Point Twilio WhatsApp webhook to `https://your-domain/api/webhook/whatsapp`.

## Production Checklist

- [ ] Replace stub auth in `app/auth.py` with real OAuth2/OIDC.
- [ ] Add `OPENAI_API_KEY` or switch to your own fine-tuned model.
- [ ] Connect `app/backend_mock.py` replacements to real OMS/EHR APIs.
- [ ] Use managed PostgreSQL instead of SQLite.
- [ ] Set strong `SECRET_KEY` and store all secrets in a vault.
- [ ] Enable HTTPS and configure CORS for known origins.
- [ ] Review HIPAA BAA (healthcare) or PCI-DSS scope (e-commerce).
