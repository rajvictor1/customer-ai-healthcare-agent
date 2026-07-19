# Deploy to Google Cloud Platform

## Cloud Run (recommended)

1. Build and push the container image:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT/customer-ai-healthcare-agent
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy customer-ai-healthcare-agent \
     --image gcr.io/PROJECT/customer-ai-healthcare-agent \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated
   ```

3. Store secrets in Secret Manager and reference them in the Cloud Run service:
   ```bash
   gcloud secrets create openai-api-key --data-file=-  # paste key
   gcloud run services update customer-ai-healthcare-agent --update-secrets=OPENAI_API_KEY=openai-api-key:latest
   ```

4. Use Cloud SQL PostgreSQL for production persistence. SQLite is ephemeral on Cloud Run and should not be used beyond local development.

## Compliance note

For healthcare workloads, ensure Google Cloud BAA is in place before enabling PHI integrations.
