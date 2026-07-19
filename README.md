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
